import re
from datetime import datetime, timedelta

from dateutil import parser
from dateutil.rrule import rrulestr
from sqlalchemy import column

from src.db.database import with_database
from src.models.api.calendar import TherapistEvents
from src.models.api.therapists import Therapist
from src.models.db.therapists import TherapistModel, AppointmentModel
from src.utils.google.google_calendar import get_events_from_gcalendar
from src.utils.settings import settings

_DATE_FORMAT = "%Y-%m-%d"


def event_to_appointment(event, therapist_model) -> AppointmentModel | None:
    if event.get("start") and event.get("end"):
        start = event["start"].get("dateTime") or event["start"].get("date")
        end = event["end"].get("dateTime") or event["end"].get("date")

        if start and end:
            appointment = AppointmentModel()
            appointment.start_date = parser.parse(start)
            appointment.end_date = parser.parse(end)
            if event.get("description"):
                match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", event["description"])
                if match:
                    email = str(match.group(0))
                    if email[-1] == ".":
                        email = email[:-1]
                    appointment.client_email = email
            if event.get("recurrence"):
                appointment.recurrence = event["recurrence"]

            appointment.therapist = therapist_model
            return appointment
    return None


def _get_therapist_model(db, name, email) -> (TherapistModel, bool):
    therapist_model = db.query(TherapistModel).filter_by(email=email).first()
    if therapist_model is not None:
        return therapist_model, True
    else:
        therapist_model = TherapistModel()
        therapist_model.name = name
        therapist_model.email = email
        db.add(therapist_model)
        return therapist_model, False


def get_appointments_for_therapist(
    db,
    therapist: Therapist,
) -> (list[AppointmentModel], list[AppointmentModel]):
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone()
    now_str = now.strftime(_DATE_FORMAT)
    now_1_weeks = now + timedelta(weeks=1)
    now_2_weeks = now + timedelta(weeks=2)
    now_2_weeks_str = now_2_weeks.strftime(_DATE_FORMAT)

    appointments = []
    first_week_appointments = []
    second_week_appointments = []

    def _proceed_appointment(item: AppointmentModel):
        if not item.start_date:
            return
        if item.recurrence:
            for rec in item.recurrence:
                rrule = rrulestr(rec, dtstart=item.start_date.astimezone())
                if len(rrule.between(now, now_1_weeks)) > 0:
                    first_week_appointments.append(item)
                if len(rrule.between(now_1_weeks, now_2_weeks)) > 0:
                    second_week_appointments.append(item)

        if now <= item.start_date.astimezone() < now_2_weeks:
            if item.start_date.astimezone() < now_1_weeks:
                first_week_appointments.append(item)
            else:
                second_week_appointments.append(item)

    therapist_model, exists = _get_therapist_model(
        db, therapist.intern_name, therapist.email
    )
    therapist_model.calendar_email = therapist.calendar_email
    if exists and therapist_model.calendar_fetched is True:
        appointments = (
            db.query(AppointmentModel)
            .filter_by(therapist_id=therapist_model.id)
            .filter(AppointmentModel.start_date.between(now_str, now_2_weeks_str))
            .all()
        )
        appointments += (
            db.query(AppointmentModel)
            .filter_by(therapist_id=therapist_model.id)
            .filter(column("recurrence").isnot(None))
            .all()
        )

        if len(appointments) != 0:
            for appointment in appointments:
                _proceed_appointment(appointment)
            return first_week_appointments, second_week_appointments

    events = get_events_from_gcalendar(
        calendar_id=settings.TEST_THERAPIST_EMAIL
        if settings.TEST_THERAPIST_EMAIL
        else therapist.calendar_email or therapist.email,
        time_min=f"{now_str}T00:00:00-00:00",
    )
    therapist_model.calendar_fetched = len(events) > 0

    for event in events:
        appointment = event_to_appointment(event, therapist_model)
        if appointment:
            appointments.append(appointment)

            if appointment.start_date and (
                now.astimezone()
                <= appointment.start_date.astimezone()
                < now_2_weeks.astimezone()
                or appointment.recurrence
            ):
                _proceed_appointment(appointment)

    db.add_all(appointments)
    return first_week_appointments, second_week_appointments


@with_database
def process_appointments(db, data: TherapistEvents):
    for therapist in data.therapists:
        therapist_model, exists = _get_therapist_model(
            db, therapist.name, therapist.email
        )
        if therapist_model:
            appointments = []
            for event in therapist.events:
                appointment = event_to_appointment(event.dict(), therapist_model)
                if appointment:
                    appointments.append(appointment)
            db.add_all(appointments)


@with_database
def delete_all_appointments(db, therapist_email: str) -> None:
    therapist = db.query(TherapistModel).filter_by(email=therapist_email).first()
    if therapist is not None:
        therapist.calendar_fetched = False
        db.query(AppointmentModel).filter_by(therapist_id=therapist.id).delete()
