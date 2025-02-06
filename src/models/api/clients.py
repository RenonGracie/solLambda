from uuid import UUID

from pydantic import BaseModel, Field
from typing import List, Any


from src.models.api.base import CustomField


class ClientShort(BaseModel):
    id: UUID | None
    first_name: str | None
    last_name: str | None
    email: str | None
    response_id: str | None


class Client(BaseModel):
    ClientId: str | None = Field(default=None)
    FirstName: str | None = Field(default=None)
    LastName: str | None = Field(default=None)
    MiddleName: str | None = Field(default=None)
    Name: str | None = Field(default=None)
    Email: str | None = Field(default=None)
    Phone: str | None = Field(default=None)
    Gender: str | None = Field(default=None)
    StateShort: str | None = Field(default=None)

    DateOfBirth: int | None = Field(default=None)
    Country: str | None = Field(default="US")

    AdditionalInformation: str | None = Field(default=None)
    CustomFields: List[CustomField] | None = Field(default=None)

    Guid: str | None = Field(default=None)
    MobilePhone: int | None = Field(default=None)
    Archived: bool | None = Field(default=None)
    Tags: List[str] | None = Field(default=None)
    PractitionerId: str | None = Field(default=None)
    LinkedClients: List[str] | None = Field(default=None)
    DateCreated: int | None = Field(default=None)
    BillingType: int | None = Field(default=None)
    LastActivityName: str | None = Field(default=None)
    CreditBalance: int | None = Field(default=None)
    LastActivityDate: int | None = Field(default=None)
    LastUpdateDate: int | None = Field(default=None)

    def __init__(self, **data: Any):
        if data.get("ClientNumber"):
            data["ClientId"] = data["ClientNumber"]
        super().__init__(**data)


class ClientQueryModel(BaseModel):
    search: str | None = None
    page: str | None = None
    dateCreatedStar: str | None = None
    dateCreatedEnd: str | None = None
    dateUpdatedStart: str | None = None
    dateUpdatedEnd: str | None = None
    externalClientId: str | None = None
    deletedOnly: bool | None = None
    IncludeProfile: bool | None = None


class Clients(BaseModel):
    clients: List[Client] | None = None


class ClientTag(BaseModel):
    ClientId: str | None = Field(...)
    Tag: str | None = Field(...)


class ClientTagQuery(BaseModel):
    clientId: str = Field(default=None)
    tag: str = Field(default=None)


class ClientPath(BaseModel):
    client_id: str = Field(...)


class ClientDiagnose(BaseModel):
    Code: str = Field(default=None)
    Description: str = Field(default=None)
    Date: str = Field(default=None)
    EndDate: str = Field(default=None)
    NoteId: str = Field(default=None)


class ClientDiagnoses(BaseModel):
    diagnoses: List[ClientDiagnose] | None = None
