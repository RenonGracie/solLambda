from pydantic import BaseModel


class Event(BaseModel):
    name: str
    params: dict


class PropertyValue(BaseModel):
    value: object


class AnalyticsEvent(BaseModel):
    client_id: str
    user_id: str | None
    timestamp_micros: int | None
    non_personalized_ads: bool | None
    events: list[Event]
    user_properties: dict[str, PropertyValue] | None
