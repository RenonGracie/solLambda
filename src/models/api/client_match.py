from pydantic import BaseModel, Field

from src.models.api.clients import ClientShort
from src.models.api.therapists import Therapist


class ClientMatch(BaseModel):
    therapist: Therapist
    score: float
    matched: list[str]


class MatchedTherapists(BaseModel):
    client: ClientShort | None
    therapists: list[ClientMatch] | None


class MatchQuery(BaseModel):
    limit: int = Field(default=10)
    response_id: str = Field(example="Client response id")
