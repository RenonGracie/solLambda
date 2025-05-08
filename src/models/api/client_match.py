from pydantic import BaseModel, Field

from src.models.api.clients import ClientShort
from src.models.api.therapists import Therapist


class ClientMatch(BaseModel):
    therapist: Therapist
    score: float
    matched_diagnoses: list[str]
    matched_specialities: list[str]


class MatchedTherapists(BaseModel):
    client: ClientShort | None
    therapists: list[ClientMatch] = []


class MatchQuery(BaseModel):
    limit: int = Field(default=10)
    last_index: int = Field(default=0)
    response_id: str = Field(example="Client response id")
