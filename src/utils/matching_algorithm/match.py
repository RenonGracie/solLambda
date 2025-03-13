import re
from typing import List

from src.db.database import with_database
from src.models.api.clients import ClientShort
from src.models.api.therapists import Therapist
from src.models.db.clients import ClientSignup
from src.utils.matching_algorithm.algorithm import calculate_match_score
from src.utils.therapist_data_utils import (
    provide_therapist_slots,
    load_therapist_media,
    implement_age_factor,
)
from src.utils.therapists.appointments_utils import get_appointments_for_therapist


@with_database
def match_client_with_therapists(
    db, response_id: str, therapists: list[Therapist], limit: int, last_index: int
) -> (ClientSignup | None, List[dict]):
    form = db.query(ClientSignup).filter_by(response_id=response_id).first()
    if not form:
        return None, []

    matches = []

    for therapist in therapists:
        score, matched_diagnoses, matched_specialities = calculate_match_score(
            form, therapist
        )
        if score >= 0:
            caseload = re.findall(r"\d+", therapist.max_caseload)
            if len(caseload) > 0:
                max_caseload = int(caseload[-1])
                if max_caseload > 0:
                    matches.append(
                        {
                            "therapist": therapist,
                            "score": score,
                            "matched_specialities": matched_specialities,
                            "matched_diagnoses": matched_diagnoses,
                            "max_caseload": max_caseload,
                        }
                    )

    matches = implement_age_factor(
        form.age,
        sorted(
            matches,
            key=lambda i: i.get("score"),
            reverse=True,
        ),
    )

    matched_therapists = []
    for match in matches:
        therapist = match["therapist"]
        max_caseload = match["max_caseload"]
        therapist.email = "melodeathmann@gmail.com"
        first_week_appointments, second_week_appointments = (
            get_appointments_for_therapist(db, therapist)
        )
        first_week_client_emails = {
            appointment.client_email for appointment in first_week_appointments
        }
        second_week_client_emails = {
            appointment.client_email for appointment in second_week_appointments
        }

        if len(first_week_client_emails) > max_caseload:
            first_week_appointments = None
        if len(second_week_client_emails) > max_caseload:
            second_week_appointments = None

        if first_week_appointments is not None or second_week_appointments is not None:
            therapist = provide_therapist_slots(
                therapist,
                first_week_appointments,
                second_week_appointments,
            )
            if len(therapist.available_slots) > 0:
                matched_therapists.append(
                    {
                        "therapist": therapist,
                        "score": match["score"],
                        "matched_specialities": match["matched_specialities"],
                        "matched_diagnoses": match["matched_diagnoses"],
                    }
                )
        if len(matched_therapists) == limit + last_index:
            break

    matched_therapists = implement_age_factor(
        form.age,
        sorted(
            matched_therapists,
            key=lambda i: (i.get("score"), len(i["therapist"].available_slots)),
            reverse=True,
        ),
    )
    return ClientShort(**form.__dict__).dict(), list(
        map(
            lambda item: load_therapist_media(db, item),
            matched_therapists[last_index : limit + last_index],
        )
    )
