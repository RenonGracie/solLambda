from datetime import datetime, timedelta
from typing import Optional

from dateutil import parser
from icalendar import Calendar, Event
from uuid import uuid4


def create_calendar_event(
    summary: str,
    start_time: str | datetime,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    location: Optional[str] = None,
    organizer_email: Optional[str] = None,
    attendee_email: Optional[str] = None,
) -> bytes:
    """
    Create an ICS calendar event

    Args:
        summary: Event title
        start_time: Event start time
        duration_minutes: Event duration in minutes
        description: Event description
        location: Event location (can be physical or virtual meeting link)
        organizer_email: Email of the event organizer
        attendee_email: Email of the attendee

    Returns:
        bytes: ICS file content
    """
    if isinstance(start_time, str):
        start_time = parser.parse(start_time)

    cal = Calendar()
    cal.add("prodid", "-//SolHealth Calendar//")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", summary)
    event.add("dtstart", start_time)
    event.add("dtend", start_time + timedelta(minutes=duration_minutes))
    event.add("dtstamp", datetime.utcnow())
    event.add("uid", str(uuid4()))

    if description:
        event.add("description", description)
    if location:
        event.add("location", location)
    if organizer_email:
        event.add("organizer", f"mailto:{organizer_email}")
    if attendee_email:
        event.add("attendee", f"mailto:{attendee_email}")

    # Add alarm/reminder 15 minutes before
    event.add(
        "alarm",
        {
            "action": "DISPLAY",
            "trigger": timedelta(minutes=-10),
            "description": "Reminder",
        },
    )

    cal.add_component(event)
    return cal.to_ical()
