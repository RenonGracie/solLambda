from datetime import datetime

from sqlalchemy import or_

from src.db.database import with_database
from src.models.db.airtable import AirtableTherapist
from src.models.db.calendar_events import CalendarEvent
from src.models.db.signup_form import ClientSignup, create_empty_client_form
from src.utils.invite_sender import send_invite
from src.utils.event_utils import (
    APPOINTMENT_EVENT_TYPE,
    send_ga_event,
)
from src.utils.google.google_calendar import (
    delete_gcalendar_event,
    update_gcalendar_event,
    get_event_from_gcalendar,
)


def _abbreviate_name(full_name, first_word_full=False):
    words = full_name.split()

    if not words:
        return ""

    if first_word_full:
        first_word = words[0]
        other_letters = [word[0].upper() for word in words[1:]]
        return f"{first_word} {' '.join(other_letters)}"
    abbreviated = [f"{word[0].upper()}." for word in words]
    return " ".join(abbreviated)


def _join_url(db, appointment: dict) -> (str | None, str | None, str | None):
    info = appointment.get("TelehealthInfo")
    if info:
        return (
            info.get("JoinUrl"),
            info.get("Invitation"),
            appointment.get("PractitionerEmail"),
        )

    service_name = appointment.get("ServiceName")
    if service_name and service_name.__contains__("Google Meets"):
        therapist = (
            db.query(AirtableTherapist)
            .filter(
                or_(
                    AirtableTherapist.email == appointment.get("PractitionerEmail"),
                    AirtableTherapist.intern_name
                    == appointment.get("PractitionerName"),
                )
            )
            .first()
        )
        if therapist:
            event = get_event_from_gcalendar(
                summary=appointment.get("ClientName"),
                calendar_id=therapist.calendar_email or therapist.email,
                date_start=appointment.get("StartDateIso"),
                date_end=appointment.get("EndDateIso"),
            )
            if event.get("conferenceData") and event.get("conferenceData").get(
                "entryPoints"
            ):
                return (
                    event.get("conferenceData").get("entryPoints")[0].get("uri"),
                    None,
                    therapist.calendar_email or therapist.email,
                )
    return None, None, None


@with_database
def process_appointment(db, data: dict):
    appointment = data["Appointment"]
    if not appointment:
        return

    client = db.query(ClientSignup).filter_by(email=appointment["ClientEmail"]).first()

    event = data["EventType"]

    if not client:
        user_id = appointment.get("ClientId")
        client = create_empty_client_form(user_id)
        client.email = appointment.get("ClientEmail")
        db.add(client)

    if event == "AppointmentCreated":
        join_url, invitation, therapist_email = _join_url(db, appointment)
        google_event = send_invite(
            therapist_name=_abbreviate_name(
                appointment["PractitionerName"], first_word_full=True
            ),
            therapist_email=therapist_email or appointment.get("PractitionerEmail"),
            client_name=_abbreviate_name(appointment["ClientName"]),
            client_email=appointment.get("ClientEmail"),
            start_time=datetime.fromtimestamp(appointment["StartDate"] / 1000),
            join_url=join_url,
            invitation=invitation,
        )
        db.add(
            CalendarEvent(
                google_calendar_id=google_event.get("id"),
                intakeQ_id=appointment.get("Id"),
            )
        )
    elif event == "AppointmentRescheduled":
        event_db = (
            db.query(CalendarEvent).filter_by(intakeQ_id=appointment.get("Id")).first()
        )
        if event_db:
            update_gcalendar_event(
                event_db.google_calendar_id,
                start_time=datetime.fromtimestamp(appointment["StartDate"] / 1000),
            )
    elif event == "AppointmentCanceled" or event == "AppointmentDeleted":
        event_db = (
            db.query(CalendarEvent).filter_by(intakeQ_id=appointment.get("Id")).first()
        )
        if event_db:
            delete_gcalendar_event(event_db.google_calendar_id)

    send_ga_event(
        client=client,
        name=event,
        params={
            "practitioner_id": appointment.get("PractitionerId"),
            "start_date": appointment.get("StartDateIso"),
            "appointment_id": appointment.get("Id"),
            "cancellation_reason": appointment.get("FullCancellationReason"),
        },
        event_type=APPOINTMENT_EVENT_TYPE,
    )
