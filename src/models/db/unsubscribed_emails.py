from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from src.models.db.base import Base


class UnsubscribedEmail(Base):
    __tablename__ = "unsubscribed_emails"

    email = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
