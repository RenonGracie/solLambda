from pydantic import BaseModel, Field


class ClientMatchData(BaseModel):
    first_name: str
    last_name: str
    state: str
    gender: str
    lived_experiences: str
    likely_therapists: str

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Your first name",
                "last_name": "Your last name",
                "state": "What state are you currently based in?",
                "gender": "Please enter your gender",
                "lived_experiences": "Are there any lived experiences you identify with that you feel are important to your match?",
                "likely_therapists": "I would like a therapist that"
            }
        }

class ClientMatch(BaseModel):
    client_name: str
    therapist_name: str
    score: float


class MatchedTherapists(BaseModel):
    matched: list[ClientMatch] | None


class MatchQuery(BaseModel):
    limit: int = Field(default=10)