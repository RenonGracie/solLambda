from pydantic import BaseModel, Field


class CustomField(BaseModel):
    FieldId: str | None = Field(default=None)
    Value: str | None = Field(default=None)
    Text: str | None = Field(default=None)


class SuccessResponse(BaseModel):
    success: bool


class Email(BaseModel):
    email: str


class Url(BaseModel):
    url: str


class EmailWithAdminPass(BaseModel):
    email: str
    admin_password: str


class AdminPass(BaseModel):
    admin_password: str
