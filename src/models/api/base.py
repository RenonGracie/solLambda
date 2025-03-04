from pydantic import BaseModel, Field


class CustomField(BaseModel):
    FieldId: str | None = Field(default=None)
    Value: str | None = Field(default=None)
    Text: str | None = Field(default=None)


class SuccessResponse(BaseModel):
    success: bool


class Email(BaseModel):
    email: str
