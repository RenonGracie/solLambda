# src/utils/matching_algorithm/match.py
import re
from datetime import datetime, timedelta

from dateutil import parser
from sqlalchemy import Column, Text

from src.db.database import with_database
from src.models.api.clients import ClientShort
from src.models.db.airtable import AirtableTherapist
from src.models.db.signup_form import ClientSignup
from src.utils.constants.contants import DATE_FORMAT
from src.utils.google.google_calendar import get_busy_events_from_gcalendar
from src.utils.logger import get_logger
from src.utils.matching_algorithm.algorithm import calculate_match_score
from src.utils.states_utils import statename_to_abbr
from src.utils.therapists.therapist_data_utils import (
    implement_age_factor,
    provide_therapist_data,
)
from src.utils.working_hours import current_working_hours, week_slots

logger = get_logger()


@with_database
def match_client_with_therapists(
    db, response_id: str, limit: int, last_index: int
) -> (ClientSignup | None, list[dict]):
    """
    Matches a client with a list of suitable therapists based on their
    preferences, payment type, and therapist availability.
    """
    form: ClientSignup = (
        db.query(ClientSignup).filter_by(response_id=response_id).first()
    )
    if not form:
        return None, []

    state = statename_to_abbr.get(form.state)

    if not form.therapist_name:
        # Build base query common for all clients
        base_query = (
            db.query(AirtableTherapist)
            .filter(
                AirtableTherapist.accepting_new_clients == True,
                Column("states", Text).like(f'%"{state}"%') if state else True,
            )
        )

        # Apply gender preference filters
        gender_filter = AirtableTherapist.gender.in_(
            ["Male"]
            if "Male" in form.therapist_identifies_as
            else ["Female"]
            if "Female" in form.therapist_identifies_as
            else ["Male", "Female"]
            if "No preference" in form.therapist_identifies_as
            else []
        )
        base_query = base_query.filter(gender_filter)

        # Apply payment type based filtering - with fallback for staging environments
        try:
            # Check if payment_type column exists and has a value
            payment_type = getattr(form, 'payment_type', 'out_of_pocket')
            if payment_type == "insurance":
                base_query = base_query.filter(AirtableTherapist.program == "Limited Permit")
            else:
                base_query = base_query.filter(
                    AirtableTherapist.program != "Limited Permit",
                    AirtableTherapist.program.isnot(None),
                )
            logger.info(
                f"Applied payment type filter for client {form.response_id}",
                extra={"payment_type": payment_type}
            )
        except AttributeError:
            # Fallback for environments where payment_type doesn't exist yet
            logger.warning(
                f"Payment type not available for client {form.response_id}, using default filtering"
            )
            base_query = base_query.filter(
                AirtableTherapist.program != "Limited Permit",
                AirtableTherapist.program.isnot(None),
            )

        therapists: list[AirtableTherapist] = base_query.all()

        logger.info(
            f"Filtered therapists for client {form.response_id}",
            extra={"therapist_count": len(therapists)}
        )
    else:
        therapist: AirtableTherapist | None = (
            db.query(AirtableTherapist)
            .filter(AirtableTherapist.intern_name == form.therapist_name)
            .first()
        )
        therapists = [therapist] if therapist else []

    matches = []

    for therapist in therapists:
        if form.therapist_name:
            if therapist.intern_name == form.therapist_name:
                matches.append(
                    {"therapist": therapist, "matched_diagnoses_specialities": []}
                )
                break
        else:
            score, matched_diagnoses_specialities = calculate_match_score(
                form, therapist
            )
            if score >= 0:
                caseload = re.findall(r"\d+", therapist.max_caseload or "0")
                if len(caseload) > 0:
                    max_caseload = int(caseload[-1])
                    if max_caseload > 0:
                        matches.append(
                            {
                                "therapist": therapist,
                                "score": score,
                                "matched_diagnoses_specialities": matched_diagnoses_specialities,
                                "max_caseload": max_caseload,
                            }
                        )

    matches = implement_age_factor(
        form.age,
        sorted(
            matches,
            key=lambda i: i.get("score", 0),
            reverse=True,
        ),
    )

    day_start, hours_count = current_working_hours()
    slots = week_slots(day_start, hours_count)

    now_2_weeks = day_start + timedelta(weeks=2)
    now_str = day_start.strftime(DATE_FORMAT)
    now_2_weeks_str = now_2_weeks.strftime(DATE_FORMAT)

    therapist_emails = [
        value["therapist"].calendar_email or value["therapist"].email
        for value in matches
    ]

    busy = get_busy_events_from_gcalendar(therapist_emails, now_str, now_2_weeks_str)
    for index in reversed(range(len(matches))):
        therapist = matches[index]["therapist"]
        if therapist:
            therapist_email = therapist.calendar_email or therapist.email
            busy_data = busy.get(therapist_email)
            if busy_data:
                busy_slots = busy_data.get("busy")
                if busy_slots:
                    available_slots = provide_therapist_slots(slots, busy_slots)
                    if len(available_slots) > 0 or form.therapist_name:
                        matches[index]["available_slots"] = available_slots
                    else:
                        del matches[index]
                else:
                     matches[index]["available_slots"] = slots # Assumes therapist is fully available
            else:
                matches[index]["available_slots"] = slots


    matched_therapists = implement_age_factor(
        form.age,
        sorted(
            matches,
            key=lambda i: (i.get("score", 0), len(i.get("available_slots", []))),
            reverse=True,
        ),
    )

    return ClientShort(**form.__dict__).dict(), list(
        map(
            lambda item: provide_therapist_data(item),
            matched_therapists[last_index : limit + last_index],
        )
    )


def _check_slot(slot: datetime, start: datetime, end: datetime) -> bool:
    start = start.astimezone()
    slot = slot.astimezone()
    end = end.astimezone()
    if start <= slot < end:
        return True
    if start <= slot + timedelta(minutes=45) < end:
        return True
    return False


def provide_therapist_slots(
    slots: list[datetime], busy_slots: list[dict]
) -> list[datetime]:
    filtered = slots[:]
    for busy_event in busy_slots:
        start = parser.parse(busy_event["start"])
        end = parser.parse(busy_event["end"])
        filtered = [dt for dt in filtered if not _check_slot(dt, start, end)]
    return filtered


def fetch_therapist_slots(email: str) -> (list | None, str | None):
    day_start, hours_count = current_working_hours()
    busy = get_busy_events_from_gcalendar(
        [email],
        day_start.strftime(DATE_FORMAT),
        (day_start + timedelta(weeks=2)).strftime(DATE_FORMAT),
    )

    slots = busy.get(email)
    if not slots:
        return week_slots(day_start, hours_count), "Could not retrieve calendar data."

    busy_slots = slots.get("busy")
    errors = slots.get("errors")
    if errors:
        return None, slots.get("errors")[0].get("reason")

    if busy_slots:
        return provide_therapist_slots(
            week_slots(day_start, hours_count), busy_slots
        ), None
    return week_slots(day_start, hours_count), None