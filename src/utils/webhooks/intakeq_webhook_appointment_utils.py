from datetime import datetime

from src.db.database import with_database
from src.models.db.calendar_events import CalendarEvent
from src.models.db.signup_form import ClientSignup, create_empty_client_form
from src.utils.email_sender import send_invite
from src.utils.event_utils import (
    send_ga_event,
    APPOINTMENT_EVENT_TYPE,
)
from src.utils.google.google_calendar import (
    update_gcalendar_event,
    delete_gcalendar_event,
)


def _abbreviate_name(full_name, first_word_full=False):
    words = full_name.split()

    if not words:
        return ""

    if first_word_full:
        first_word = words[0]
        other_letters = [word[0].upper() for word in words[1:]]
        return f"{first_word} {' '.join(other_letters)}"
    else:
        abbreviated = [f"{word[0].upper()}." for word in words]
        return " ".join(abbreviated)


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

    if (
        appointment.get("ClientEmail") == "alinaadelaida5@gmail.com"
        or appointment.get("PractitionerEmail") == "alinakostyuk05@gmail.com"
    ):
        if event == "AppointmentCreated":
            google_event = send_invite(
                therapist_name=_abbreviate_name(
                    appointment["PractitionerName"], first_word_full=True
                ),
                therapist_email=appointment.get("PractitionerEmail"),
                client_name=_abbreviate_name(appointment["ClientName"]),
                client_email=appointment.get("ClientEmail"),
                start_time=datetime.fromtimestamp(appointment["StartDate"] / 1000),
                telehealth_info=appointment.get("TelehealthInfo"),
            )
            db.add(
                CalendarEvent(
                    google_calendar_id=google_event.get("id"),
                    intakeQ_id=appointment.get("Id"),
                )
            )
        elif event == "AppointmentRescheduled":
            event_db = (
                db.query(CalendarEvent)
                .filter_by(intakeQ_id=appointment.get("Id"))
                .first()
            )
            if event_db:
                update_gcalendar_event(
                    event_db.google_calendar_id,
                    start_time=datetime.fromtimestamp(appointment["StartDate"] / 1000),
                )
        elif event == "AppointmentCancelled" or event == "AppointmentDeleted":
            event_db = (
                db.query(CalendarEvent)
                .filter_by(intakeQ_id=appointment.get("Id"))
                .first()
            )
            if event_db:
                delete_gcalendar_event(event_db.google_calendar_id)

    send_ga_event(
        database=db,
        client=client,
        name=event,
        value=appointment.get("Id"),
        var_2=appointment.get("FullCancellationReason"),
        params={
            "ClientId": appointment["ClientId"],
            "PractitionerId": appointment.get("PractitionerId"),
        },
        event_type=APPOINTMENT_EVENT_TYPE,
    )
