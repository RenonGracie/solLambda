from datetime import timedelta

from dateutil import parser
from flask import jsonify
from sqlalchemy import or_

from src.db.database import db
from src.models.api.appointments import CreateAppointment
from src.models.api.error import Error
from src.models.db.airtable import AirtableTherapist
from src.models.db.signup_form import ClientSignup
from src.utils.constants.contants import DATE_FORMAT
from src.utils.event_utils import CALL_SCHEDULED_EVENT, USER_EVENT_TYPE, send_ga_event
from src.utils.google.google_calendar import get_busy_events_from_gcalendar
from src.utils.intakeq.appointments import check_therapist_availability
from src.utils.intakeq.clients import reassign_client, search_client
from src.utils.logger import get_logger
from src.utils.request_utils import (
    create_appointment,
    get_booking_settings,
    search_appointments,
)

logger = get_logger()


def book_appointment(body: CreateAppointment):
    result = get_booking_settings()
    if not result:
        logger.error("Unable to get booking settings")
        return jsonify(Error(error="Unable to get booking settings").dict()), 400
    practitioners = result.json()["Practitioners"]
    sessions = result.json()["Services"]

    therapist_email = body.therapist_email.lower()
    try:
        therapist = next(
            item
            for item in practitioners
            if str(item["Email"]).lower() == body.therapist_email
            or (item["CompleteName"]).lower() == body.therapist_name.lower()
        )
    except StopIteration:
        therapist = None
    if not therapist:
        logger.error("Therapist not found")
        return jsonify(Error(error="Therapist not found").dict()), 404

    slot_time = parser.parse(body.datetime)

    therapist_model: AirtableTherapist = (
        db.query(AirtableTherapist)
        .filter(
            or_(
                AirtableTherapist.email == therapist_email,
                AirtableTherapist.intern_name == body.therapist_name,
            )
        )
        .first()
    )

    if not therapist_model.accepting_new_clients:
        return jsonify(
            Error(error="Therapist is not accepting new clients").dict()
        ), 410

    form = db.query(ClientSignup).filter_by(response_id=body.client_response_id).first()
    if not form:
        logger.error(
            "Signup form not found",
            extra={"client_response_id": body.client_response_id},
        )
        return jsonify(
            Error(
                error=f"Signup form with id '{body.client_response_id}' not found"
            ).dict()
        ), 404

    name = f"{form.first_name} {form.last_name}"

    client = search_client(form.email, name)

    if not client:
        logger.error(
            f"Client with name '{form.first_name} {form.last_name}' not found on intakeQ"
        )
        return jsonify(
            Error(
                error=f"Client with name '{form.first_name} {form.last_name}' not found on intakeQ"
            ).dict()
        ), 404
    client_id = client.get("ClientId") or client.get("ClientNumber")

    busy = get_busy_events_from_gcalendar(
        [therapist_model.calendar_email or therapist_model.email],
        slot_time - timedelta(days=1),
        slot_time + timedelta(days=1),
    )

    result = search_appointments(
        {
            "practitionerEmail": therapist_email,
            "startDate": (slot_time - timedelta(days=1)).strftime(DATE_FORMAT),
            "endDate": (slot_time + timedelta(days=1)).strftime(DATE_FORMAT),
        }
    )
    error = check_therapist_availability(
        slot_time, result.json() if result.status_code == 200 else [], True
    )

    if not error:
        slots = busy.get(therapist_model.calendar_email or therapist_model.email)
        busy_slots = slots.get("busy")
        if busy_slots:
            error = check_therapist_availability(slot_time, busy_slots)

    if error:
        return jsonify(Error(error=error).dict()), 409

    try:
        match form.discount:
            case 100:
                session_id = next(
                    session
                    for session in sessions
                    if str(session["Name"]).__eq__(
                        "First Session (Free) (Google Meets)"
                        if therapist_email.endswith("@solhealth.co")
                        else "First Session (Free)"
                    )
                )["Id"]
            case 50:
                session_id = next(
                    session
                    for session in sessions
                    if str(session["Name"]).__eq__(
                        "First Session (Promo Code) (Google Meets)"
                        if therapist_email.endswith("@solhealth.co")
                        else "First Session (Promo Code)"
                    )
                )["Id"]
            case _:
                session_id = next(
                    session
                    for session in sessions
                    if str(session["Name"]).__eq__(
                        "First Session (Google Meets)"
                        if therapist_email.endswith("@solhealth.co")
                        else "First Session"
                    )
                )["Id"]
    except StopIteration:
        session_id = "eeb06bd5-c63b-4615-bc98-e2e80268ec6f"

    result = create_appointment(
        {
            "PractitionerId": therapist["Id"],
            "ClientId": client_id,
            "LocationId": "1",
            "UtcDateTime": int(slot_time.timestamp() * 1000),
            "ServiceId": session_id,
            "SendClientEmailNotification": body.send_client_email_notification,
            "ReminderType": body.reminder_type if body.reminder_type else "Email",
            "Status": body.status,
        }
    )
    json = result.json()

    if result.status_code == 200:
        send_ga_event(
            client=form,
            name=CALL_SCHEDULED_EVENT,
            params={"appointment_id": json.get("Id")},
            event_type=USER_EVENT_TYPE,
        )
    reassign_client(client, therapist["Id"])

    return jsonify(json), result.status_code
