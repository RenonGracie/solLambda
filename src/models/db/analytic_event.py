import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, String, Text

from src.models.db.base import Base


class AnalyticEvent(Base):
    __tablename__ = "analytic_event"

    id = Column("id", UUID, primary_key=True, default=uuid4)
    created_at = Column("created_at", DateTime, default=datetime.now())
    client_id = Column("client_id", String(100), nullable=True)
    email = Column("email", String(255), nullable=True)
    user_id = Column("user_id", String(100), nullable=True)
    session_id = Column("session_id", String(100), nullable=True)
    type = Column("type", String(255), nullable=True)
    name = Column("name", Text)
    value = Column("value", Text, nullable=True)
    _params = Column("params", Text, nullable=True)
    var_1 = Column("var_1", Text, nullable=True)
    var_2 = Column("var_2", Text, nullable=True)

    utm_source = Column("utm_source", Text, nullable=True)
    utm_medium = Column("utm_medium", Text, nullable=True)
    utm_campaign = Column("utm_campaign", Text, nullable=True)
    utm_adid = Column("utm_adid", Text, nullable=True)
    utm_adgroup = Column("utm_adgroup", Text, nullable=True)
    utm_content = Column("utm_content", Text, nullable=True)
    utm_term = Column("utm_term", Text, nullable=True)

    clid = Column("clid", Text, nullable=True)

    @property
    def params(self) -> dict:
        return json.loads(self._params or "{}")

    @params.setter
    def params(self, sources: dict):
        self._params = json.dumps(sources)
