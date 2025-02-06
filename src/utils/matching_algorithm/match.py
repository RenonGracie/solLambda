from typing import List

from src.db.database import db
from src.models.api.therapist_s3 import S3MediaType
from src.models.api.therapists import Therapist
from src.models.db.clients import ClientSignup
from src.utils import s3
from src.utils.matching_algorithm.algorithm import calculate_match_score


def _load_therapist_media(data: dict) -> dict:
    email = data['therapist']['email']
    data['therapist']['welcome_video_link'] = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.WELCOME_VIDEO
    )
    data['therapist']['image_link'] = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.IMAGE
    )
    return data


def sort(e: dict):
    return e.get("score")


def match_client_with_therapists(
    response_id: str, therapists: list[Therapist], limit: int
) -> (ClientSignup | None, List[dict]):
    form = db.query(ClientSignup).filter_by(response_id=response_id).first()
    if not form:
        return None, []

    matches = []

    for therapist in therapists:
        score, matched = calculate_match_score(form, therapist)
        if score >= 0:
            matches.append(
                {"therapist": therapist.dict(), "score": score, "matched": matched}
            )

    matches.sort(key=sort, reverse=True)
    return form, list(map(lambda item: _load_therapist_media(item), matches[:limit]))
