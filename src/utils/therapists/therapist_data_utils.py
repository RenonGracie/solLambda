from src.models.api.therapist_s3 import S3MediaType
from src.utils import s3
from src.utils.logger import get_logger
from src.utils.settings import settings

logger = get_logger()


def _rearrange_elements(elements, indices):
    selected_elements = [elements[i] for i in indices if i < len(elements)]
    remaining_elements = [
        elem for idx, elem in enumerate(elements) if idx not in indices
    ]
    rearranged_elements = selected_elements + remaining_elements
    return rearranged_elements


def _find_client_age_group(client_age):
    if 20 <= client_age <= 26:
        return "Early/Mid 20s"
    elif 27 <= client_age <= 29:
        return "Late 20s"
    elif 30 <= client_age <= 39:
        return "30s"
    elif 40 <= client_age <= 49:
        return "40s"
    elif 50 <= client_age <= 59:
        return "50s"
    elif client_age >= 60:
        return "60+"
    else:
        return "Age out of range"


def implement_age_factor(age_str: str, matched: list[dict]) -> list[dict]:
    try:
        age = int(age_str)
        suitable = []
        for i in range(len(matched)):
            data = matched[i]
            if str(data["therapist"].age).__eq__(_find_client_age_group(age)):
                suitable.append(i)
                if len(suitable) >= 3:
                    break

        if len(suitable):
            matched = _rearrange_elements(matched, suitable)

        return matched
    except ValueError:
        return matched


def provide_therapist_data(data: dict) -> dict:
    therapist_model = data["therapist"]
    email = (
        settings.TEST_THERAPIST_EMAIL
        if settings.TEST_THERAPIST_EMAIL
        else therapist_model.email
    )
    therapist = therapist_model.to_therapist()
    therapist.available_slots = data["available_slots"]
    data.pop("available_slots")

    if not therapist.welcome_video_link and settings.TEST_WELCOME_VIDEO:
        therapist.welcome_video_link = settings.TEST_WELCOME_VIDEO
    if not therapist.greetings_video_link and settings.TEST_GREETINGS_VIDEO:
        therapist.greetings_video_link = settings.TEST_GREETINGS_VIDEO

    therapist.image_link = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.IMAGE
    )
    data["therapist"] = therapist.dict()
    return data
