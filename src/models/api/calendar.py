from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


class Attendee(BaseModel):
    responseStatus: str | None
    email: str | None
    organizer: Optional[bool]
    attendeeself: Optional[bool]


class Key(BaseModel):
    type: str | None


class ConferenceSolution(BaseModel):
    name: str | None
    key: Key | None
    iconUri: str | None


class EntryPoint(BaseModel):
    entryPointType: str | None
    label: str | None
    uri: str | None


class ConferenceData(BaseModel):
    entryPoints: List[EntryPoint] | None
    conferenceId: str | None
    conferenceSolution: ConferenceSolution | None


class EventCreator(BaseModel):
    creatorself: bool | None
    email: str | None


class EvendDate(BaseModel):
    dateTime: str | None
    timeZone: str | None


class Reminders(BaseModel):
    useDefault: bool | None


class CalendarEvent(BaseModel):
    summary: str | None
    reminders: Reminders | None
    creator: EventCreator | None
    kind: str | None
    htmlLink: str | None
    created: str | None
    attendees: List[Attendee] | None
    iCalUID: str | None
    start: EvendDate | None
    hangoutLink: str | None
    eventType: str | None
    sequence: int | None
    organizer: EventCreator | None
    conferenceData: ConferenceData | None
    etag: str | None
    end: EvendDate | None
    id: str | None
    updated: datetime | None
    status: str | None


class CalendarEvents(BaseModel):
    events: List[CalendarEvent] | None


class EventQuery(BaseModel):
    calendar_id: str
    time_min: str = Field(default=None)
    time_max: str = Field(default=None)
    max_results: int = Field(default=None)
