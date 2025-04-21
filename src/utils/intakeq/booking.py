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
from src.utils.email_sender import EmailSender
from src.utils.event_utils import send_ga_event, CALL_SCHEDULED_EVENT, USER_EVENT_TYPE
from src.utils.intakeq.appointments import check_therapist_availability
from src.utils.intakeq.clients import search_client, reassign_client
from src.utils.logger import get_logger
from src.utils.request_utils import (
    get_booking_settings,
    search_appointments,
    create_appointment,
)
from src.utils.webhooks.intakeq_webhook_appointment_utils import (
    update_appointment_with_db,
)

logger = get_logger()

email_sender = EmailSender()


def book_appointment(base_url: str, body: CreateAppointment):
    result = get_booking_settings()
    if not result:
        logger.error("Unable to get booking settings")
        return jsonify(Error(error="Unable to get booking settings").dict()), 400
    practitioners = result.json()["Practitioners"]
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

    therapist_email = therapist.get("Email")
    slot_time = parser.parse(body.datetime)
    result = search_appointments(
        {
            "practitionerEmail": therapist_email,
            "startDate": (slot_time - timedelta(days=1)).strftime(DATE_FORMAT),
            "endDate": (slot_time + timedelta(days=1)).strftime(DATE_FORMAT),
        }
    )
    if result.status_code == 200:
        appointments = result.json()
    else:
        appointments = []
    appointment, error = check_therapist_availability(slot_time, appointments)

    therapist_model = (
        db.query(AirtableTherapist)
        .filter(
            or_(
                AirtableTherapist.email == therapist_email,
                AirtableTherapist.intern_name == body.therapist_name,
            )
        )
        .first()
    )

    utm = form.utm
    email = form.email
    if appointment and therapist_model:
        update_appointment_with_db(therapist_model, appointment)

    if error:
        return jsonify(Error(error=error).dict()), 409

    result = create_appointment(
        {
            "PractitionerId": therapist["Id"],
            "ClientId": client_id,
            "LocationId": "1",
            "UtcDateTime": int(slot_time.timestamp() * 1000),
            "ServiceId": "e818ad3d-5758-4a7d-a1f9-657af8ac4dc8"
            if form.promo_code and len(form.promo_code) > 1
            else "099e964f-c444-4c68-9668-00f734b95afd",
            "SendClientEmailNotification": body.send_client_email_notification,
            "ReminderType": body.reminder_type if body.reminder_type else "Email",
            "Status": body.status,
        }
    )
    json = result.json()

    if result.status_code == 200:
        if therapist_model:
            update_appointment_with_db(therapist_model, json)

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

    email_sender.send_email(
        base_url,
        therapist_name=f"{therapist.get('FirstName')} {therapist.get('LastName')[:1]}",
        therapist_email=therapist_email,
        client_name=f"{client.get('FirstName')[:1]}.{(client.get('LastName') or ' ')[:1]}",
        client_email=client.get("Email"),
        start_time=slot_time,
    )

    return jsonify(json), result.status_code
