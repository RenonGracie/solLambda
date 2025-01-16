from pydantic import BaseModel, Field
from typing import List, Any


class CustomField(BaseModel):
    FieldId: str = Field()
    Value: str = Field()
    Text: str = Field()


class User(BaseModel):
    ClientId: int = Field()
    FirstName: str = Field()
    LastName: str = Field()
    Gender: str = Field()
    Email: str = Field()
    Phone: str = Field()
    StateShort: str = Field()

    DateOfBirth: int = Field()
    Country: str = Field(default='US')

    AdditionalInformation: str = Field()
    CustomFields: List[CustomField] = Field()

    def __init__(self, **data: Any):
        super().__init__(**data)
