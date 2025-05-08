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

    client = db.query(ClientSignup).filter_by(email=appointment["ClientEmail"]).first()

    event = data["EventType"]

    if not client:
        user_id = appointment.get("ClientId")
        client = create_empty_client_form(user_id)
        client.email = appointment.get("ClientEmail")
        db.add(client)

    send_ga_event(
        database=db,
        client=client,
        name=event,
        value=appointment.get("Id"),
        var_2=appointment.get("FullCancellationReason"),
        params={
            "ClientId": appointment["ClientId"],
            "PractitionerId": appointment["PractitionerId"],
        },
        event_type=APPOINTMENT_EVENT_TYPE,
    )
