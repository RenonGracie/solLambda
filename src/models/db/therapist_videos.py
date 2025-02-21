from uuid import uuid4

from sqlalchemy import Column, Text, String
from sqlalchemy.dialects.postgresql import UUID

from src.models.db.base import Base


class TherapistVideoModel(Base):
    __tablename__ = "therapist_videos"

    id = Column("id", UUID, primary_key=True, default=uuid4)
    name = Column("name", Text)
    email = Column("email", Text, unique=True)
    video_url = Column("video_url", Text, unique=True)
    type = Column("type", String(50), unique=True)
