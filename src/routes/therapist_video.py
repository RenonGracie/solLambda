from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint
from pyairtable import Api

from src.db.database import db, with_database
from src.models.api.base import AdminPass
from src.models.api.therapist_videos import TherapistVideos, TherapistVideo
from src.models.db.therapist_videos import TherapistVideoModel
from src.utils.settings import settings

__tag = Tag(name="Therapist Videos")
therapist_video_api = APIBlueprint(
    "therapist_videos",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/therapist_videos",
)

api = Api(settings.AIRTABLE_API_KEY)


@therapist_video_api.get(
    "", responses={200: TherapistVideos}, summary="Get all therapist's videos"
)
def get_videos():
    videos = db.query(TherapistVideoModel).all()
    return jsonify(
        {"videos": [TherapistVideo(**video.__dict__).dict() for video in videos]}
    ), 200


@with_database
def _save_video(database, video: TherapistVideos):
    database.add_all([TherapistVideoModel(**video.dict()) for video in video.videos])


@therapist_video_api.post(
    "", responses={200: TherapistVideos}, summary="Set therapist's videos"
)
def set_videos(query: AdminPass, body: TherapistVideos):
    if not query.admin_password.__eq__(settings.ADMIN_PASSWORD):
        return jsonify({}), 401
    else:
        _save_video(body)

        return jsonify(body.dict()), 200


@with_database
def _update_video(database, video: TherapistVideo) -> bool:
    model = (
        database.query(TherapistVideoModel)
        .filter_by(email=video.email, type=video.type)
        .first()
    )
    if not model:
        return False
    model.email = video.email
    return True


@therapist_video_api.patch(
    "", responses={200: TherapistVideo}, summary="Update therapist's video"
)
def update_video(query: AdminPass, body: TherapistVideo):
    if not query.admin_password.__eq__(settings.ADMIN_PASSWORD):
        return jsonify({}), 401
    else:
        if not _update_video(body):
            return jsonify({}), 404
        return jsonify(body.dict()), 200
