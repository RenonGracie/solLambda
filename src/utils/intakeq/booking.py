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
from src.utils.email_sender import EmailSender, send_invite
from src.utils.event_utils import send_ga_event, CALL_SCHEDULED_EVENT, USER_EVENT_TYPE
from src.utils.google.google_calendar import get_busy_events_from_gcalendar
from src.utils.intakeq.appointments import check_therapist_availability
from src.utils.intakeq.clients import search_client, reassign_client
from src.utils.logger import get_logger
from src.utils.request_utils import (
    get_booking_settings,
    create_appointment,
    search_appointments,
)

logger = get_logger()

email_sender = EmailSender()


def book_appointment(base_url: str, body: CreateAppointment):
    result = get_booking_settings()
    if not result:
        logger.error("Unable to get booking settings")
        return jsonify(Error(error="Unable to get booking settings").dict()), 400
    practitioners = result.json()["Practitioners"]
    sessions = result.json()["Services"]
    try:
        therapist = next(
            item
            for item in practitioners
            if str(item["Email"]).lower() == body.therapist_email.lower()
            or (item["CompleteName"]).lower() == body.therapist_name.lower()
        )
    except StopIteration:
        therapist = None
    if not therapist:
        logger.error("Therapist not found")
        return jsonify(Error(error="Therapist not found").dict()), 404

    therapist_email = therapist.get("Email")
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

    utm = form.utm
    email = form.email

    try:
        match form.discount:
            case 100:
                session_id = next(
                    session
                    for session in sessions
                    if str(session["Name"]).__eq__("First Session (Free)")
                )["Id"]
            case 50:
                session_id = next(
                    session
                    for session in sessions
                    if str(session["Name"]).__eq__("First Session (Promo Code)")
                )["Id"]
            case _:
                session_id = next(
                    session
                    for session in sessions
                    if str(session["Name"]).__eq__("First Session")
                )["Id"]
    except StopIteration:
        session_id = "099e964f-c444-4c68-9668-00f734b95afd"

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
            client_id=utm.get("client_id"),
            name=CALL_SCHEDULED_EVENT,
            value=json.get("Id"),
            user_id=utm.get("user_id"),
            session_id=utm.get("session_id"),
            event_type=USER_EVENT_TYPE,
            email=email,
        )
    reassign_client(client, therapist["Id"])

    send_invite(
        therapist_name=f"{therapist.get('FirstName')} {(therapist.get('LastName') or '')[:1]}",
        therapist_email=therapist_email,
        client_name=f"{client.get('FirstName')[:1]}.{(client.get('LastName') or ' ')[:1]}",
        client_email=client.get("Email"),
        start_time=slot_time,
        telehealth_info=json.get("TelehealthInfo"),
    )

    return jsonify(json), result.status_code
