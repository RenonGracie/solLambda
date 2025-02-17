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

    therapist_id = mapped_column(ForeignKey("therapists.id"))
    therapist = relationship("TherapistModel", back_populates="appointments")
