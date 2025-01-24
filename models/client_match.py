from pydantic import BaseModel, Field


class ClientMatchData(BaseModel):
    first_name: str = Field(example = "Your first name")
    last_name: str = Field(example = "Your last name")
    state: str = Field(example = "What state are you currently based in?")
    gender: str = Field(example = "Please enter your gender")
    lived_experiences: str = Field(example = "Are there any lived experiences you identify with that you feel are important to your match?")
    likely_therapists: str = Field(example = "I would like a therapist that")

class ClientMatch(BaseModel):
    client_name: str
    therapist_name: str
    score: float


class MatchedTherapists(BaseModel):
    matched: list[ClientMatch] | None


class MatchQuery(BaseModel):
    limit: int = Field(default=10)