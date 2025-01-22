from pydantic import BaseModel

class TherapistsTableObject(BaseModel):
    createdTime: str
    id: str
    fields: dict

class TherapistsTable(BaseModel):
    table: list[TherapistsTableObject]