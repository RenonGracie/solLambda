import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor
from typing import List

from dateutil import parser
from dateutil.rrule import rrulestr
from sqlalchemy import delete

from src.db.database import with_database, drop_appointments
from src.models.api.calendar import TherapistEvents
from src.models.db.airtable import AirtableTherapist
from src.models.db.appointments import AppointmentModel
from src.utils.google.google_calendar import get_events_from_gcalendar
from src.utils.settings import settings


_BATCH_SIZE = 20


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


def _get_therapist_model(db, email) -> AirtableTherapist | None:
    return db.query(AirtableTherapist).filter_by(email=email).first()


def _process_appointment_batch(
    appointments: List[AppointmentModel], now, now_1_weeks, now_2_weeks
):
    first_week = []
    second_week = []

    for item in appointments:
        if not item.start_date:
            continue

        if item.start.tzinfo is None:
            start = item.start
            current_now = now.replace(tzinfo=None)
            current_now_1_weeks = now_1_weeks.replace(tzinfo=None)
            current_now_2_weeks = now_2_weeks.replace(tzinfo=None)
        else:
            start = item.start.astimezone()
            current_now = now.astimezone()
            current_now_1_weeks = now_1_weeks.astimezone()
            current_now_2_weeks = now_2_weeks.astimezone()

        if item.recurrence:
            for rec in item.recurrence:
                rrule = rrulestr(rec, dtstart=start)
                if len(rrule.between(current_now, current_now_1_weeks)) > 0:
                    first_week.append(item)
                if len(rrule.between(current_now_1_weeks, current_now_2_weeks)) > 0:
                    second_week.append(item)
        else:
            if current_now <= start < current_now_2_weeks:
                if start < current_now_1_weeks:
                    first_week.append(item)
                else:
                    second_week.append(item)

    return first_week, second_week


def get_appointments_for_therapist(
    db,
    now,
    therapist: AirtableTherapist,
    appointments: list[AppointmentModel],
) -> (list[AppointmentModel], list[AppointmentModel]):
    now_1_weeks = now + timedelta(weeks=1)
    now_2_weeks = now + timedelta(weeks=2)

    first_week_appointments = []
    second_week_appointments = []

    db.autoflush = False
    try:
        if appointments:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for i in range(0, len(appointments), _BATCH_SIZE):
                    batch = appointments[i : i + _BATCH_SIZE]
                    futures.append(
                        executor.submit(
                            _process_appointment_batch,
                            batch,
                            now,
                            now_1_weeks,
                            now_2_weeks,
                        )
                    )

                for future in futures:
                    first_week, second_week = future.result()
                    first_week_appointments.extend(first_week)
                    second_week_appointments.extend(second_week)

            return first_week_appointments, second_week_appointments

        fetched = events_from_calendar_to_appointments(
            settings.TEST_THERAPIST_EMAIL
            if settings.TEST_THERAPIST_EMAIL
            else therapist.calendar_email or therapist.email,
            now,
        )

        if fetched:
            appointments = [app for app in fetched if app]

            for appointment in appointments:
                appointment.therapist = therapist
                db.add(appointment)

            db.flush()

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for i in range(0, len(appointments), _BATCH_SIZE):
                    batch = appointments[i : i + _BATCH_SIZE]
                    futures.append(
                        executor.submit(
                            _process_appointment_batch,
                            batch,
                            now,
                            now_1_weeks,
                            now_2_weeks,
                        )
                    )

                for future in futures:
                    first_week, second_week = future.result()
                    first_week_appointments.extend(first_week)
                    second_week_appointments.extend(second_week)

    finally:
        db.autoflush = True

    return first_week_appointments, second_week_appointments


def events_from_calendar_to_appointments(
    calendar_id: str, now: datetime = datetime.now()
) -> list[AppointmentModel | None]:
    _DATE_FORMAT = "%Y-%m-%d"
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
    therapist_model = _get_therapist_model(db, therapist.email)
    if therapist_model:
        appointments = []
        for event in therapist.events:
            appointment = event_to_appointment(event)
            if appointment:
                appointment.therapist = therapist_model
                appointments.append(appointment)
        db.add_all(appointments)


@with_database
def delete_all_appointments(db, therapist_email: str) -> None:
    if therapist_email.__eq__("*"):
        drop_appointments()
    else:
        therapist = db.query(AirtableTherapist).filter_by(email=therapist_email).first()
        if therapist is not None:
            db.execute(
                delete(AppointmentModel).where(
                    AppointmentModel.therapist_id == therapist.id
                )
            )
            db.commit()
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
