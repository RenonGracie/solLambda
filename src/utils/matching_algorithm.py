from typing import List

from fuzzywuzzy import fuzz

from src.db.database import db
from src.models.api.therapists import Therapist
from src.models.db.clients import ClientSignup


def calculate_match_score(data: ClientSignup, therapist: Therapist) -> (int, list):
    # Hard factor #1
    if data.state.lower() not in [state.lower() for state in therapist.states]:
        return -1, []

    # Hard factor #2
    if (
        data.i_would_like_therapist.__contains__("Is male")
        and not str(therapist.gender).lower().__eq__("male")
    ) or (
        data.i_would_like_therapist.__contains__("Is female")
        and not str(therapist.gender).lower().__eq__("female")
    ):
        return -1, []

    # Hard factor #3
    ph9 = data.ph9_sum
    yes_count = str(therapist.experience_with_risk_clients).lower().count("yes")
    if ph9 > 20 and yes_count < 2:
        return -1, []
    elif ph9 > 14 and yes_count < 1:
        return -1, []

    gad7 = data.gad7_sum
    if gad7 >= 15 and yes_count < 1:
        return -1, []

    last_ph9 = data.suicidal_thoughts.points
    if last_ph9 >= 2 > yes_count:
        return -1, []
    elif last_ph9 >= 1 > yes_count:
        return -1, []

    score = 0
    matched_diagnoses = []
    matched_specialities = []

    # Soft factor #1
    for preference in data.i_would_like_therapist:
        for diagnose in therapist.diagnoses:
            if fuzz.token_set_ratio(preference, diagnose) > 80:
                score += 3
                matched_diagnoses.append(diagnose)
        for speciality in therapist.specialities:
            if fuzz.token_set_ratio(preference, speciality) > 80:
                score += 3
                matched_specialities.append(speciality)
    # Soft factor #2
    for lived_experience in data.lived_experiences:
        if lived_experience.lower().__contains__(
            "non-traditional"
        ) and therapist.family_household.lower().__contains__("non-traditional"):
            score += 2
        if lived_experience.__contains__(
            "generation immigrant"
        ) and therapist.immigration_background.lower().__contains__("gen immigrant"):
            score += 2
        if lived_experience.lower().__contains__(
            "individualist"
        ) and therapist.culture.lower().__contains__("individualist"):
            score += 2
        if lived_experience.lower().__contains__(
            "collectivist"
        ) and therapist.culture.lower().__contains__("collectivist"):
            score += 2
        if lived_experience.lower().__contains__(
            "many places"
        ) and therapist.places.lower().__contains__("many places"):
            score += 2
        if lived_experience.lower().__contains__("caretaker role") and (
            therapist.married or therapist.has_children
        ):
            score += 2
        if lived_experience.__contains__("as LGBTQ+") and therapist.lgbtq_part:
            score += 2
        if (
            lived_experience.lower().__contains__("affected by social media")
            and therapist.negative_affect_by_social_media
        ):
            score += 2

    return score, matched_diagnoses[:1] + matched_specialities[:2]


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
    return form, matches[:limit]
