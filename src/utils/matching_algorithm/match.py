import re
from datetime import datetime, timedelta

from dateutil import parser
from sqlalchemy import Column, Text

from src.db.database import with_database
from src.models.api.clients import ClientShort
from src.models.api.typeform import TypeformData # Added import for TypeformData
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

# Assuming these imports are necessary for the new function.
# You may need to adjust the paths based on your project structure.
from src.utils.external_apis.intakeq import intakeq
from src.utils.external_apis.google_analytics import send_ga_event
from src.utils.client_data_utils import (
    create_client_model,
    create_new_form,
    create_from_typeform_data,
)
from src.utils.db_utils import save_update_client
from src.config import settings # Assuming a settings file for constants
from src.utils.constants.events import REGISTRATION_EVENT, USER_EVENT_TYPE

logger = get_logger()


@with_database
def process_typeform_data(db, response_json: dict):
    """
    Processes incoming webhook data from Typeform, creates or updates a client,
    and triggers downstream actions like IntakeQ and analytics events.
    This version handles both insurance and out-of-pocket payment types,
    including logic for pre-existing insurance clients.
    """
    response_id = response_json["form_response"]["token"]

    if db.query(ClientSignup).filter_by(response_id=response_id).first():
        logger.warning(f"Duplicate Typeform submission received: {response_id}")
        return

    form_response = response_json["form_response"]
    hidden = form_response.get("hidden", {})

    # Extract payment type from Typeform hidden fields, defaulting to out_of_pocket
    payment_type = hidden.get("paymentType", "out_of_pocket")

    # Extract client ID for insurance clients (created during eligibility check)
    existing_client_id = hidden.get("clientId", None)

    questions_json = form_response["definition"]["fields"]
    questions = dict(map(lambda item: (item["ref"], item), questions_json))
    answers = form_response["answers"]
    json: dict = {}
    for answer in answers:
        question = questions[answer["field"]["ref"]]
        json[question["id"]] = {
            "ref": answer["field"]["ref"],
            "answer": answer[answer["type"]]
            if answer["type"] != "multiple_choice"
            else answer["choices"],
            "title": question["title"],
            "type": question["type"],
        }
    data = TypeformData(json, form_response.get("variables"))

    form = create_from_typeform_data(response_id, data)
    # Save payment type on the form
    form.payment_type = payment_type
    if form.state.__eq__("I don't see my state"):
        db.add(form)
        db.commit() # Commit and exit early if state is not supported
        return

    # Create / update the IntakeQ client in the relevant account
    if payment_type == "insurance" and existing_client_id:
        # For insurance clients, we already have the profile, just need to update it
        client_json = {"Id": existing_client_id, "ClientId": existing_client_id}
        user_id = existing_client_id
    else:
        # For out-of-pocket, create new client
        response = save_update_client(
            create_client_model(form).dict(), payment_type=payment_type
        )
        client_json = response.json()
        user_id = client_json.get("Id") or client_json.get("ClientId") or response_id

    # Store UTM params against the user/client
    form.setup_utm(user_id, hidden)

    logger.debug("intakeQ response", extra={"response": client_json if payment_type == "out_of_pocket" else {"existing_client": existing_client_id}})

    # Send data to IntakeQ bot for BOTH payment types
    user_data = create_new_form(form)

    # Add additional fields for the bot
    user_data["payment_type"] = payment_type
    user_data["existing_client_id"] = existing_client_id # Will be None for out-of-pocket

    # Add insurance-specific hidden fields if present
    if payment_type == "insurance":
        user_data["insurance_provider"] = hidden.get("insuranceProvider", "")
        user_data["member_id"] = hidden.get("memberId", "")

    intakeq(
        {
            "user": user_data,
            "spreadsheet_id": settings.SPREADSHEET_ID,
            "form_url": settings.INTAKEQ_SIGNUP_FORM,
            "env": "live" if settings.ENV == "prod" else settings.ENV,
            "response_id": response_id,
            "payment_type": payment_type, # Pass payment type to bot
        },
        payment_type=payment_type,
    )

    # Persist form to DB
    db.add(form)
    db.commit() # Commit the new client to the database

    # Send Google Analytics event with payment_type param
    send_ga_event(
        client=form,
        name=REGISTRATION_EVENT,
        params={"payment_type": payment_type},
        event_type=USER_EVENT_TYPE,
    )
    logger.info(f"Successfully processed Typeform submission for client {user_id}")


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

        # Apply payment type based filtering
        if form.payment_type == "insurance":
            base_query = base_query.filter(AirtableTherapist.program == "Limited Permit")
        else:
            base_query = base_query.filter(
                AirtableTherapist.program != "Limited Permit",
                AirtableTherapist.program.isnot(None),
            )

        therapists: list[AirtableTherapist] = base_query.all()

        logger.info(
            f"Filtered therapists for client {form.response_id} based on payment_type={form.payment_type}",
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
                caseload = re.findall(r"\d+", therapist.max_caseload)
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
            key=lambda i: i.get("score"),
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