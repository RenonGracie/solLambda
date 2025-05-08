from uuid import uuid4

from sqlalchemy import Column, UUID, String

from src.models.db.base import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_event"

    id = Column("id", UUID, primary_key=True, default=uuid4)
    google_calendar_id = Column("google_calendar_id", String(100), nullable=True)
    intakeQ_id = Column("intakeQ_id", String(100), nullable=True)
