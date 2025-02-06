from enum import Enum

from pydantic import BaseModel


class S3MediaType(Enum):
    IMAGE = "image"
    WELCOME_VIDEO = "welcome_video"
    INTRO_VIDEO = "intro_video"


class MediaQuery(BaseModel):
    email: str
    type: S3MediaType


class MediaLink(BaseModel):
    url: str
