import re
from datetime import datetime, timedelta
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event

from sqlalchemy import Column, Text, column

from src.db.database import with_database
from src.models.api.clients import ClientShort
from src.models.db.airtable import AirtableTherapist
from src.models.db.appointments import AppointmentModel
from src.models.db.signup_form import ClientSignup
from src.utils.constants.contants import DEFAULT_ZONE, DATE_FORMAT
from src.utils.matching_algorithm.algorithm import calculate_match_score
from src.utils.states_utils import statename_to_abbr
from src.utils.therapists.therapist_data_utils import (
    provide_therapist_slots,
    provide_therapist_data,
    implement_age_factor,
)
from src.utils.therapists.appointments_utils import get_appointments_for_therapist


@with_database
def match_client_with_therapists(
    db, response_id: str, limit: int, last_index: int
) -> (ClientSignup | None, List[dict]):
    form: ClientSignup = (
        db.query(ClientSignup).filter_by(response_id=response_id).first()
    )
    if not form:
        return None, []

    state = statename_to_abbr.get(form.state)

    therapists = (
        db.query(AirtableTherapist)
        .filter(
            AirtableTherapist.accepting_new_clients,
            Column("states", Text).like(f'%"{state}"%') if state else True,
            AirtableTherapist.gender.in_(
                ["Male"]
                if "Male" in form.therapist_identifies_as
                else ["Female"]
                if "Female" in form.therapist_identifies_as
                else ["Male", "Female"]
                if "No preference" in form.therapist_identifies_as
                else []
            ),
        )
        .all()
    )

    matches = []

    for therapist in therapists:
        if form.therapist_name:
            if therapist.intern_name == form.therapist_name:
                matches.append(
                    {
                        "therapist": therapist,
                    }
                )
                break
        else:
            score, matched_diagnoses, matched_specialities = calculate_match_score(
                form, therapist
            )
            if score >= 0:
                caseload = re.findall(r"\d+", therapist.max_caseload)
                if len(caseload) > 0:
                    max_caseload = int(caseload[-1])
                    if max_caseload > 0:
                        matches.append(
                            {
                                "therapist": therapist,
                                "score": score,
                                "matched_specialities": matched_specialities,
                                "matched_diagnoses": matched_diagnoses,
                                "max_caseload": max_caseload,
                            }
                        )

    matches = implement_age_factor(
        form.age,
        sorted(
            matches,
            key=lambda i: i.get("score"),
            reverse=True,
        ),
    )

    first_week_slots = []
    second_week_slots = []
    now = datetime.now(tz=DEFAULT_ZONE).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    for day in range(7):
        for hour in range(15):
            first_week_slots.append(now + timedelta(hours=hour, days=day))
            second_week_slots.append(now + timedelta(hours=hour, days=day + 7))

    now_2_weeks = now + timedelta(weeks=2)
    now_str = now.strftime(DATE_FORMAT)
    now_2_weeks_str = now_2_weeks.strftime(DATE_FORMAT)

    therapist_ids = [value["therapist"].id for value in matches]

    all_appointments = (
        db.query(AppointmentModel)
        .filter(AppointmentModel.therapist_id.in_(therapist_ids))
        .filter(
            (AppointmentModel.start_date.between(now_str, now_2_weeks_str))
            | (column("recurrence").isnot(None))
        )
        .all()
    )

    def get_therapist_appointments_async(session, therapist_item):
        appointments = [
            appointment
            for appointment in all_appointments
            if appointment.therapist_id == therapist_item.id
        ]
        first_week_appointments, second_week_appointments = (
            get_appointments_for_therapist(session, now, therapist_item, appointments)
        )
        first_week_client_emails = {
            appointment.client_email for appointment in first_week_appointments
        }
        second_week_client_emails = {
            appointment.client_email for appointment in second_week_appointments
        }
        return {
            "therapist": therapist_item,
            "first_week_appointments": first_week_appointments,
            "second_week_appointments": second_week_appointments,
            "first_week_client_emails": first_week_client_emails,
            "second_week_client_emails": second_week_client_emails,
        }

    def process_matches(session, matches_data, signup_form, limit_value, last):
        """Process matches using ThreadPoolExecutor"""
        matched = []
        stop_event = Event()

        if matches_data:
            with ThreadPoolExecutor(max_workers=min(10, len(matches_data))) as executor:
                # Create future for each therapist
                future_to_therapist = {
                    executor.submit(
                        get_therapist_appointments_async, session, match["therapist"]
                    ): match
                    for match in matches_data
                }

                # Process results as they complete
                for future in as_completed(future_to_therapist):
                    if stop_event.is_set():
                        break

                    match = future_to_therapist[future]
                    try:
                        therapist_data = future.result()
                        therapist_item = therapist_data["therapist"]
                        caseload_value = match.get("max_caseload")

                        first_week_appointments: list | None = therapist_data[
                            "first_week_appointments"
                        ]
                        second_week_appointments: list | None = therapist_data[
                            "second_week_appointments"
                        ]

                        if (
                            caseload_value
                            and len(therapist_data["first_week_client_emails"])
                            > caseload_value
                        ):
                            first_week_appointments = None
                        if (
                            caseload_value
                            and len(therapist_data["second_week_client_emails"])
                            > caseload_value
                        ):
                            second_week_appointments = None

                        if (
                            first_week_appointments is not None
                            or second_week_appointments is not None
                            or therapist_item.intern_name == signup_form.therapist_name
                        ):
                            available_slots = provide_therapist_slots(
                                now,
                                first_week_slots,
                                second_week_slots,
                                first_week_appointments,
                                second_week_appointments,
                            )
                            if len(available_slots) > 0:
                                matched.append(
                                    {
                                        "therapist": therapist_item,
                                        "score": match.get("score"),
                                        "matched_specialities": match.get(
                                            "matched_specialities"
                                        ),
                                        "matched_diagnoses": match.get(
                                            "matched_diagnoses"
                                        ),
                                        "available_slots": available_slots,
                                    }
                                )
                                print("matched_therapists", len(matched))

                        if len(matched) == limit_value + last:
                            print("limit reached")
                            stop_event.set()
                            for f in future_to_therapist:
                                if not f.done():
                                    f.cancel()
                            break

                    except Exception as e:
                        therapist_id = (
                            match["therapist"].id
                            if match and "therapist" in match
                            else "unknown"
                        )
                        print(f"Error processing therapist {therapist_id}: {str(e)}")
                        continue

        return matched

    matched_therapists = process_matches(db, matches, form, limit, last_index)
    print("next steps")
    matched_therapists = implement_age_factor(
        form.age,
        sorted(
            matched_therapists,
            key=lambda i: (i.get("score"), len(i["available_slots"])),
            reverse=True,
        ),
    )

    return ClientShort(**form.__dict__).dict(), list(
        map(
            lambda item: provide_therapist_data(item),
            matched_therapists[last_index : limit + last_index],
        )
    )
