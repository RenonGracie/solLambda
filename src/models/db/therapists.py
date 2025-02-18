import json
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.db.base import Base


class TherapistModel(Base):
    __tablename__ = "therapists"

    id = Column("id", UUID, primary_key=True, default=uuid4)
    name = Column("name", Text)
    email = Column("email", String(100), unique=True)


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column("id", String(100), primary_key=True)

    intakeq_id = Column("intakeq_id", String(100))

    start_date = Column("start_date", DateTime)
    end_date = Column("end_date", DateTime)

    client_email = Column("client_emails", Text)

    _recurrence = Column("recurrence", Text)

    therapist_id = Column("therapist_id", UUID, nullable=True)
    therapist = relationship(
        "TherapistModel",
        foreign_keys=[therapist_id],
        primaryjoin="TherapistModel.id == AppointmentModel.therapist_id",
    )

    @property
    def recurrence(self):
        return json.loads(self._recurrence or "[]")

    @recurrence.setter
    def recurrence(self, sources):
        self._recurrence = json.dumps(sources)
