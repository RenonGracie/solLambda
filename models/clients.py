from pydantic import BaseModel, Field
from typing import List, Any


class CustomField(BaseModel):
    FieldId: str = Field(default=None)
    Value: str = Field(default=None)
    Text: str = Field(default=None)


class Client(BaseModel):
    ClientId: int = Field(default=None)
    FirstName: str = Field(default=None)
    LastName: str = Field(default=None)
    MiddleName: str = Field(default=None)
    Name: str = Field(default=None)
    Email: str = Field(default=None)
    Phone: str = Field(default=None)
    Gender: str = Field(default=None)
    StateShort: str = Field(default=None)

    DateOfBirth: int = Field(default=None)
    Country: str = Field(default='US')

    AdditionalInformation: str = Field(default=None)
    CustomFields: List[CustomField] = Field(default=None)

    Guid: str = Field(default=None)
    MobilePhone: int = Field(default=None)
    Archived: bool = Field(default=None)
    Tags: List[str] = Field(default=None)
    PractitionerId: str = Field(default=None)
    LinkedClients: List[str] = Field(default=None)
    DateCreated: int = Field(default=None)
    BillingType: int = Field(default=None)
    LastActivityName: str = Field(default=None)
    CreditBalance: int = Field(default=None)
    LastActivityDate: int = Field(default=None)
    LastUpdateDate: int = Field(default=None)

    def __init__(self, **data: Any):
        if data.get('ClientNumber'):
            data['ClientId'] = data['ClientNumber']
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
    ClientId: str | None = Field(..., example='123')
    Tag: str | None = Field(..., example='text')

class ClientTagQuery(BaseModel):
    clientId: str = Field(default=None, example='123')
    tag: str = Field(default=None, example='text')

class ClientPath(BaseModel):
    client_id: int = Field(..., description='client id')

class ClientDiagnose(BaseModel):
    Code: str = Field(default=None, example='1')
    Description: str = Field(default=None, example='Alcohol Disorder')
    Date: str = Field(default=None, example='2021-12-08T23:00:00Z')
    EndDate: str = Field(default=None, example=None)
    NoteId: str = Field(default=None, example='82328bc2-3ff8-4ea8...')

class ClientDiagnoses(BaseModel):
    diagnoses: List[ClientDiagnose] | None = None