from pydantic import BaseModel


class VideoQuery(BaseModel):
    video_id: str


class VideoLink(BaseModel):
    url: str
