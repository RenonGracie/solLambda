import re
from datetime import datetime, timedelta

from dateutil import parser

from src.db.database import db
from src.models.api.therapists import Therapist
from src.models.db.therapists import TherapistModel, AppointmentModel
from src.utils.google_calendar import get_events_from_gcalendar

_DATE_FORMAT = "%Y-%m-%d"


def get_appointments_for_therapist(
    therapist: Therapist,
) -> (list[AppointmentModel], list[AppointmentModel]):
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now_str = now.strftime(_DATE_FORMAT)
    now_1_weeks = now + timedelta(weeks=1)
    now_2_weeks = now + timedelta(weeks=2)
    now_2_weeks_str = now_2_weeks.strftime(_DATE_FORMAT)

    appointments = []
    first_week_appointments = []
    second_week_appointments = []

    def _proceed_appointment(item: AppointmentModel):
        if now.astimezone() <= item.start_date.astimezone() < now_2_weeks.astimezone():
            if item.start_date.astimezone() < now_1_weeks.astimezone():
                first_week_appointments.append(item)
            else:
                second_week_appointments.append(item)

    therapist_model = db.query(TherapistModel).filter_by(email=therapist.email).first()
    if therapist_model is not None:
        appointments = (
            db.query(AppointmentModel)
            .filter_by(therapist_id=therapist_model.id)
            .filter(AppointmentModel.start_date.between(now_str, now_2_weeks_str))
            .all()
        )

        for appointment in appointments:
            _proceed_appointment(appointment)
        return first_week_appointments, second_week_appointments

    therapist_model = TherapistModel()
    therapist_model.name = therapist.intern_name
    therapist_model.email = therapist.email
    db.add(therapist_model)

    events = get_events_from_gcalendar(
        calendar_id=therapist.email,
        time_max=f"{now_2_weeks_str}T00:00:00-00:00",
        time_min=f"{now_str}T00:00:00-00:00",
    )
    for event in events:
        start = event["start"].get("dateTime")
        end = event["end"].get("dateTime")
        appointment = AppointmentModel(id=event["id"])
        if start:
            appointment.start_date = parser.parse(start)
        if end:
            appointment.end_date = parser.parse(end)
        if event["description"]:
            match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", event["description"])
            if match:
                email = str(match.group(0))
                if email[-1] == ".":
                    email = email[:-1]
                appointment.client_email = email

        appointment.therapist = therapist_model
        appointments.append(appointment)

        if (
            appointment.start_date
            and now.astimezone()
            <= appointment.start_date.astimezone()
            < now_2_weeks.astimezone()
        ):
            _proceed_appointment(appointment)

    db.add_all(appointments)
    db.commit()
    return first_week_appointments, second_week_appointments
