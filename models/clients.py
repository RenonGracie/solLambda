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
    Gender: str = Field(default=None)
    Email: str = Field(default=None)
    Phone: str = Field(default=None)
    StateShort: str = Field(default=None)

    DateOfBirth: int = Field(default=None)
    Country: str = Field(default='US')

    AdditionalInformation: str = Field(default=None)
    CustomFields: List[CustomField] = Field(default=None)

    Guid: str = Field(default=None)
    MobilePhone: int = Field(default=None)
    Name: str = Field(default=None)
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
        super().__init__(**data)
