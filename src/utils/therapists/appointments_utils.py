import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil import parser
from dateutil.rrule import rrulestr
from sqlalchemy import column, delete

from src.db.database import with_database, drop_appointments
from src.models.api.calendar import TherapistEvents
from src.models.api.therapists import Therapist
from src.models.db.therapists import TherapistModel, AppointmentModel
from src.utils.google.google_calendar import get_events_from_gcalendar
from src.utils.settings import settings

_DATE_FORMAT = "%Y-%m-%d"


def _is_offset_within_tolerance(dt, zone, max_diff_hours=1) -> bool:
    if zone.startswith("GMT") or zone.startswith("UTC"):
        return False
    date_offset = dt.utcoffset().total_seconds() if dt.utcoffset() else 0
    tz_offset = dt.astimezone(ZoneInfo(zone)).utcoffset().total_seconds()
    diff_hours = abs(date_offset - tz_offset) / 3600
    return diff_hours <= max_diff_hours


def event_to_appointment(event) -> AppointmentModel | None:
    if event.get("start") and event.get("end"):
        start = None
        start_zone = None
        end = None
        end_zone = None

        if "dateTime" in event["start"] and "dateTime" in event["end"]:
            date_time = event["start"].get("dateTime")
            zone = event["start"].get("timeZone")
            start = parser.parse(date_time)
            if zone == "GMT-04:00":
                pass
            if _is_offset_within_tolerance(start, zone):
                start_zone = zone

            date_time = event["end"].get("dateTime")
            zone = event["end"].get("timeZone")
            if zone == "GMT-04:00":
                pass
            end = parser.parse(date_time)
            if _is_offset_within_tolerance(start, zone):
                end_zone = zone

        if "date" in event["start"] and "date" in event["end"]:
            start = parser.parse(event["start"].get("date"))
            end = parser.parse(event["end"].get("date"))

        if start and end:
            appointment = AppointmentModel()
            appointment.start_date = start
            appointment.start_zone = start_zone
            appointment.end_date = end
            appointment.end_zone = end_zone
            if event.get("description"):
                match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", event["description"])
                if match:
                    email = str(match.group(0))
                    if email[-1] == ".":
                        email = email[:-1]
                    appointment.client_email = email
            if event.get("recurrence"):
                appointment.recurrence = event["recurrence"]
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
                rrule = rrulestr(rec, dtstart=item.start.astimezone())
                if len(rrule.between(now, now_1_weeks)) > 0:
                    first_week_appointments.append(item)
                if len(rrule.between(now_1_weeks, now_2_weeks)) > 0:
                    second_week_appointments.append(item)

        if now <= item.start.astimezone() < now_2_weeks:
            if item.start.astimezone() < now_1_weeks:
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

    fetched = events_from_calendar_to_appointments(
        settings.TEST_THERAPIST_EMAIL
        if settings.TEST_THERAPIST_EMAIL
        else therapist.calendar_email or therapist.email,
        now,
    )
    therapist_model.calendar_fetched = len(fetched) > 0

    for appointment in fetched:
        if appointment:
            appointment.therapist = therapist_model
            appointments.append(appointment)

            if appointment.start_date and (
                now.astimezone()
                <= appointment.start.astimezone()
                < now_2_weeks.astimezone()
                or appointment.recurrence
            ):
                _proceed_appointment(appointment)

    db.add_all(appointments)
    return first_week_appointments, second_week_appointments


def events_from_calendar_to_appointments(
    calendar_id: str, now: datetime = datetime.now()
) -> list[AppointmentModel | None]:
    print("Fetch from calendar", calendar_id)
    now_str = now.strftime(_DATE_FORMAT)
    events = get_events_from_gcalendar(
        calendar_id=calendar_id,
        time_min=f"{now_str}T00:00:00-00:00",
    )

    return [event_to_appointment(event) for event in events]


@with_database
def process_appointments(db, data: TherapistEvents):
    therapist = data.therapist
    therapist_model, exists = _get_therapist_model(db, therapist.name, therapist.email)
    if therapist_model:
        appointments = []
        for event in therapist.events:
            appointment = event_to_appointment(event)
            if appointment:
                appointment.therapist = therapist_model
                appointments.append(appointment)
        therapist_model.calendar_fetched = True
        db.add_all(appointments)


@with_database
def delete_all_appointments(db, therapist_email: str) -> None:
    if therapist_email.__eq__("*"):
        drop_appointments()
        therapists = db.query(TherapistModel).all()
        for therapist in therapists:
            therapist.calendar_fetched = False
    else:
        therapist = db.query(TherapistModel).filter_by(email=therapist_email).first()
        if therapist is not None:
            db.execute(
                delete(AppointmentModel).where(
                    AppointmentModel.therapist_id == therapist.id
                )
            )
            db.commit()
            therapist.calendar_fetched = False
            print(
                "Therapist",
                therapist_email,
                "appointments count",
                len(
                    db.query(AppointmentModel)
                    .filter_by(therapist_id=therapist.id)
                    .all()
                ),
            )
