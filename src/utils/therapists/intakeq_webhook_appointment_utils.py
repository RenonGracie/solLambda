from dateutil import parser
from sqlalchemy import and_

from src.db.database import db
from src.models.db.therapists import TherapistModel, AppointmentModel


def _create_appointment(therapist: TherapistModel, data: dict):
    appointment = AppointmentModel()
    appointment.intakeq_id = data["Id"]
    appointment.start_date = parser.parse(data["StartDateIso"])
    appointment.end_date = parser.parse(data["EndDateIso"])
    appointment.client_email = data["ClientEmail"]
    appointment.therapist = therapist
    db.add(appointment)


def _update_appointment(therapist: TherapistModel, data: dict):
    appointment = (
        db.query(AppointmentModel).filter_by(intakeq_id=data["Id"]).first()
    )
    if appointment is None:
        _create_appointment(therapist, data)
    else:
        appointment.start_date = parser.parse(data["StartDateIso"])
        appointment.end_date = parser.parse(data["EndDateIso"])


def _delete_appointment(data: dict):
    appointment = (
        db.query(AppointmentModel).filter_by(intakeq_id=data["Id"]).first()
    )
    if appointment is None:
        start_date = parser.parse(data["StartDateIso"])
        end_date = parser.parse(data["EndDateIso"])
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


def process_appointment(data: dict):
    appointment = data["Appointment"]
    therapist_model = (
        db.query(TherapistModel)
        .filter_by(email=appointment["PractitionerEmail"])
        .first()
    )

    if therapist_model is None:
        therapist_model = TherapistModel()
        therapist_model.name = appointment["PractitionerName"]
        therapist_model.email = appointment["PractitionerEmail"]
        db.add(therapist_model)

    match data["EventType"]:
        case "AppointmentCreated":
            _create_appointment(therapist_model, appointment)
        case "AppointmentRescheduled":
            _update_appointment(therapist_model, appointment)
        case "AppointmentDeleted":
            _delete_appointment(appointment)

    db.commit()
