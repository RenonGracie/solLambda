from datetime import datetime

from pydantic import BaseModel
from pydantic.types import UUID4


class AnalyticsEventQuery(BaseModel):
    client_id: str | None
    email: str | None
    user_id: str | None
    session_id: str | None
    event_type: str | None
    value: str | None
    name: str | None
    var_1: str | None
    var_2: str | None

    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    utm_adid: str | None
    utm_adgroup: str | None
    utm_content: str | None
    utm_term: str | None

    clid: str | None


class AnalyticsEvent(AnalyticsEventQuery):
    id: UUID4
    created_at: datetime | None
    params: dict | None
    value: str | None


class AnalyticsEvents(BaseModel):
    events: list[AnalyticsEvent]
