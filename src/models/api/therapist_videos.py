from pydantic import BaseModel


class TherapistVideo(BaseModel):
    name: str | None
    email: str | None
    video_url: str
    type: str


class TherapistVideos(BaseModel):
    videos: list[TherapistVideo]
