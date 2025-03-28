from pydantic import BaseModel


class Error(BaseModel):
    error: str
    details: list[dict] | None = None
