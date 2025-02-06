from typing import List

from pydantic import BaseModel

from src.models.api.clients import ClientShort


class ClientForms(BaseModel):
    forms: List[ClientShort]


class ClientFormQuery(BaseModel):
    response_id: str | None
