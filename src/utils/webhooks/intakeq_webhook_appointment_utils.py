from datetime import datetime, UTC

from sqlalchemy import and_

from src.db.database import with_database
from src.models.db.clients import ClientSignup
from src.models.db.therapists import TherapistModel, AppointmentModel
from src.utils.event_utils import send_ga_event, INTAKEQ_EVENT_TYPE
from src.utils.str_utils import camel_to_snake_case


def _create_appointment(db, therapist: TherapistModel, data: dict):
    appointment = AppointmentModel()
    appointment.intakeq_id = data["Id"]
    appointment.start_date = datetime.fromtimestamp(data["StartDate"] / 1e3, UTC)
    appointment.end_date = datetime.fromtimestamp(data["EndDate"] / 1e3, UTC)
    appointment.client_email = data["ClientEmail"]
    appointment.therapist = therapist
    db.add(appointment)


def _update_appointment(db, therapist: TherapistModel, data: dict):
    appointment = db.query(AppointmentModel).filter_by(intakeq_id=data["Id"]).first()
    if appointment is None:
        _create_appointment(db, therapist, data)
    else:
        appointment.start_date = datetime.fromtimestamp(data["StartDate"] / 1e3, UTC)
        appointment.end_date = datetime.fromtimestamp(data["EndDate"] / 1e3, UTC)


def _delete_appointment(db, data: dict):
    appointment = db.query(AppointmentModel).filter_by(intakeq_id=data["Id"]).first()
    if appointment is None:
        start_date = datetime.fromtimestamp(data["StartDate"] / 1e3, UTC)
        end_date = datetime.fromtimestamp(data["EndDate"] / 1e3, UTC)
        appointment = (
            db.query(AppointmentModel)
            .filter(
                and_(
                    AppointmentModel.start_date == start_date,
                    AppointmentModel.end_date == end_date,
                )
            )
            .first()
        )

    if appointment:
        db.delete(appointment)


@with_database
def process_appointment(db, data: dict):
    appointment = data["Appointment"]
    therapist_model = (
        db.query(TherapistModel)
        .filter_by(email=appointment["PractitionerEmail"])
        .first()
    )

    client = db.query(ClientSignup).filter_by(email=appointment["ClientEmail"]).first()

    if therapist_model is None:
        therapist_model = TherapistModel()
        therapist_model.name = appointment["PractitionerName"]
        therapist_model.email = appointment["PractitionerEmail"]
        db.add(therapist_model)

    event = data["EventType"]
    match event:
        case "AppointmentCreated":
            _create_appointment(db, therapist_model, appointment)
        case "AppointmentRescheduled":
            _update_appointment(db, therapist_model, appointment)
        case "AppointmentDeleted":
            _delete_appointment(db, appointment)

    if client:
        send_ga_event(
            client_id=client.utm.get("client_id"),
            user_id=client.utm.get("user_id"),
            session_id=client.utm.get("session_id"),
            name=camel_to_snake_case(event),
            value=appointment.get("Id"),
            params={
                "therapist_id": appointment["PractitionerId"],
            },
            event_type=INTAKEQ_EVENT_TYPE,
        )
