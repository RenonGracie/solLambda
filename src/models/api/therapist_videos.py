from enum import Enum

from pydantic import BaseModel


class VideoType(Enum):
    WELCOME = "welcome"
    GREETING = "greeting"


class TherapistVideo(BaseModel):
    name: str | None
    email: str | None
    video_url: str
    type: VideoType

    class Config:
        use_enum_values = True

    def __init__(self, **data):
        data["type"] = VideoType(data["type"])
        super().__init__(**data)


class TherapistVideos(BaseModel):
    videos: list[TherapistVideo]
