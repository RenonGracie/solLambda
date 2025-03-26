from typing import List

from pydantic import BaseModel


class CalendarEvent(BaseModel):
    start: str | None
    end: str | None
    event: str | None
    zone: str | None
    description: str | None
    recurrence: list[str] | None


class CalendarEventsDateGroup(BaseModel):
    date: str
    events: List[CalendarEvent]


class CalendarEvents(BaseModel):
    data: List[CalendarEventsDateGroup] | None


class EventQuery(BaseModel):
    calendar_id: str
    date_min: str | None
    date_max: str | None
    max_results: int | None


class TherapistEmails(BaseModel):
    emails: list[str]


class TherapistEvents(BaseModel):
    class TherapistEvent(BaseModel):
        name: str
        email: str
        calendar_email: str | None
        events: list[dict]

    therapist: TherapistEvent
