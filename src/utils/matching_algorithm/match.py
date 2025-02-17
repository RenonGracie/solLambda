import re
from typing import List

from src.db.database import db
from src.models.api.therapist_s3 import S3MediaType
from src.models.api.therapists import Therapist, Appointment
from src.models.db.clients import ClientSignup
from src.utils import s3
from src.utils.matching_algorithm.algorithm import calculate_match_score
from src.utils.settings import settings
from src.utils.therapists.appointments_utils import get_appointments_for_therapist


def _load_therapist_media(therapist: Therapist) -> dict:
    email = therapist.email
    therapist.welcome_video_link = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.WELCOME_VIDEO
    )
    therapist.image_link = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.IMAGE
    )
    return therapist.dict()


def match_client_with_therapists(
    response_id: str, therapists: list[Therapist], limit: int, last_index: int
) -> (ClientSignup | None, List[dict]):
    form = db.query(ClientSignup).filter_by(response_id=response_id).first()
    if not form:
        return None, []

    matches = []

    for therapist in therapists:
        score, matched = calculate_match_score(form, therapist)
        if score >= 0:
            caseload = re.findall(r"\d+", therapist.max_caseload)
            if len(caseload) > 0:
                max_caseload = int(caseload[-1])
                if max_caseload > 0:
                    if settings.TEST_THERAPIST_EMAIL:
                        therapist.email = settings.TEST_THERAPIST_EMAIL

                    first_week_appointments, second_week_appointments = (
                        get_appointments_for_therapist(therapist)
                    )
                    first_week_client_emails = {
                        appointment.client_email
                        for appointment in first_week_appointments
                    }
                    second_week_client_emails = {
                        appointment.client_email
                        for appointment in second_week_appointments
                    }
                    if (
                        len(first_week_client_emails) <= max_caseload
                        or len(second_week_client_emails) <= max_caseload
                    ):
                        therapist.free_slots = 2 * max_caseload - (
                            len(first_week_client_emails)
                            + len(second_week_client_emails)
                        )
                        therapist.appointments = [
                            Appointment(**appointment.__dict__)
                            for appointment in (
                                first_week_appointments + second_week_appointments
                            )
                        ]
                        matches.append(
                            {"therapist": therapist, "score": score, "matched": matched}
                        )

    matches = sorted(
        matches, key=lambda i: (i.get("score"), i["therapist"].free_slots), reverse=True
    )
    return form, list(
        map(
            lambda item: _load_therapist_media(item["therapist"]),
            matches[last_index : limit + last_index],
        )
    )
