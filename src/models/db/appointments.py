import json
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.fields.custom import DateTimeAsString
from src.models.db.base import Base


class AppointmentModel(Base):
    __tablename__ = "therapist_appointments"

    id = Column("id", UUID, primary_key=True, default=uuid4)

    intakeq_id = Column("intakeq_id", String(100))

    start_date = Column("start_date", DateTimeAsString(32))
    start_zone = Column("start_zone", String(30), nullable=True)
    end_date = Column("end_date", DateTimeAsString(32))
    end_zone = Column("end_zone", String(30), nullable=True)

    client_email = Column("client_emails", Text)

    _recurrence = Column("recurrence", Text)

    therapist_id = Column("therapist_id", String(100), nullable=True)
    therapist = relationship(
        "AirtableTherapist",
        foreign_keys=[therapist_id],
        primaryjoin="AirtableTherapist.id == AppointmentModel.therapist_id",
    )

    @property
    def start(self):
        return (
            self.start_date
            if self.start_zone is None
            else self.start_date.replace(tzinfo=ZoneInfo(self.start_zone))
        )

    @property
    def end(self):
        return (
            self.end_date
            if self.end_zone is None
            else self.end_date.replace(tzinfo=ZoneInfo(self.end_zone))
        )

    @property
    def recurrence(self):
        return json.loads(self._recurrence or "[]")

    @recurrence.setter
    def recurrence(self, sources):
        self._recurrence = json.dumps(sources)
