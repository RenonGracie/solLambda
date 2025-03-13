from uuid import uuid4

from sqlalchemy import Column, Text, String
from sqlalchemy.dialects.postgresql import UUID

from src.models.db.base import Base


class TherapistVideoModel(Base):
    __tablename__ = "therapist_video_links"

    id = Column("id", UUID, primary_key=True, default=uuid4)
    name = Column("name", Text)
    email = Column("email", Text)
    video_url = Column("video_url", Text)
    type = Column("type", String(50))
