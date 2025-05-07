from src.db.database import with_database
from src.models.db.airtable import AirtableTherapist
from src.models.db.signup_form import ClientSignup, create_empty_client_form
from src.utils.event_utils import (
    send_ga_event,
    APPOINTMENT_EVENT_TYPE,
)


@with_database
def process_appointment(db, data: dict):
    appointment = data["Appointment"]
    therapist_model = (
        db.query(AirtableTherapist)
        .filter_by(email=appointment["PractitionerEmail"])
        .first()
    )

    client = db.query(ClientSignup).filter_by(email=appointment["ClientEmail"]).first()

    if therapist_model is None:
        return

    event = data["EventType"]

    if not client:
        user_id = appointment.get("ClientId")
        client = create_empty_client_form(user_id)
        db.add(client)

    send_ga_event(
        database=db,
        client_id=client.utm.get("client_id"),
        user_id=client.utm.get("user_id"),
        email=client.email,
        session_id=client.utm.get("session_id"),
        name=event,
        value=appointment.get("Id"),
        var_2=appointment.get("FullCancellationReason"),
        params={
            "ClientId": appointment["ClientId"],
            "PractitionerId": appointment["PractitionerId"],
        },
        event_type=APPOINTMENT_EVENT_TYPE,
    )
