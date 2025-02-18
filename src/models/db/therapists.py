import json
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column

from src.models.db.base import Base


class TherapistModel(Base):
    __tablename__ = "therapists"

    id = Column("id", UUID, primary_key=True, default=uuid4)
    name = Column("name", Text)
    email = Column("email", String(100), unique=True)

    appointments = relationship("AppointmentModel", back_populates="therapist")


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column("id", String(100), primary_key=True)

    intakeq_id = Column("intakeq_id", String(100))

    start_date = Column("start_date", DateTime)
    end_date = Column("end_date", DateTime)

    client_email = Column("client_emails", Text)

    _recurrence = Column("recurrence", Text)

    therapist_id = Column(UUID(as_uuid=True), index=True)  # Убрали FK
    therapist = relationship("TherapistModel", primaryjoin="foreign(AppointmentModel.therapist_id) == TherapistModel.id", back_populates="appointments")

    @property
    def recurrence(self):
        return json.loads(self._recurrence or "[]")

    @recurrence.setter
    def recurrence(self, sources):
        self._recurrence = json.dumps(sources)
