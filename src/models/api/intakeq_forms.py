from pydantic import BaseModel


class IntakeQMandatoryFormQuery(BaseModel):
    client_id: str
    therapist_id: str
