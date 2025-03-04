from enum import Enum

from pydantic import BaseModel

from src.models.api.base import Email


class S3MediaType(Enum):
    IMAGE = "image"
    WELCOME_VIDEO = "welcome_video"
    INTRO_VIDEO = "intro_video"


class MediaQuery(Email):
    type: S3MediaType


class MediaLink(BaseModel):
    url: str
