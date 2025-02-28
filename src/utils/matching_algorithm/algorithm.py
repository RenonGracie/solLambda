from fuzzywuzzy import fuzz

from src.models.api.therapists import Therapist
from src.models.db.clients import ClientSignup


def calculate_match_score(
    data: ClientSignup, therapist: Therapist
) -> (int, list, list):
    # Hard factor #1
    if not therapist.states or data.state.lower() not in [
        state.lower() for state in therapist.states
    ]:
        return -1, []

    # Hard factor #2
    if therapist.gender and (
        (
            data.i_would_like_therapist.__contains__("Is male")
            and str(therapist.gender).lower().__eq__("male")
        )
        or (
            data.i_would_like_therapist.__contains__("Is female")
            and str(therapist.gender).lower().__eq__("female")
        )
    ):
        pass
    else:
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

    last_ph9 = data.suicidal_thoughts_points
    if last_ph9 >= 2 > yes_count:
        return -1, []
    elif last_ph9 >= 1 > yes_count:
        return -1, []

    score = 0
    matched_diagnoses = []
    matched_specialities = []

    # Soft factor #1
    for preference in data.i_would_like_therapist:
        if therapist.diagnoses:
            for diagnose in therapist.diagnoses:
                if fuzz.partial_token_set_ratio(preference, diagnose) > 80:
                    score += 3
                    matched_diagnoses.append(diagnose)
        if therapist.specialities:
            for speciality in therapist.specialities:
                print()
                if fuzz.partial_token_set_ratio(preference, speciality) > 80:
                    score += 3
                    matched_specialities.append(speciality)
        if therapist.therapeutic_orientation:
            for therapeutic_orientation in therapist.therapeutic_orientation:
                if (
                    fuzz.partial_token_set_ratio(preference, therapeutic_orientation)
                    > 80
                ):
                    score += 3

    # Soft factor #2
    for lived_experience in data.lived_experiences:
        if (
            therapist.family_household
            and lived_experience.lower().__contains__("non-traditional")
            and therapist.family_household.lower().__contains__("non-traditional")
        ):
            score += 2
        if (
            therapist.immigration_background
            and lived_experience.__contains__("generation immigrant")
            and therapist.immigration_background.lower().__contains__("gen immigrant")
        ):
            score += 2
        if (
            therapist.culture
            and lived_experience.lower().__contains__("individualist")
            and therapist.culture.lower().__contains__("individualist")
        ):
            score += 2
        if (
            therapist.culture
            and lived_experience.lower().__contains__("collectivist")
            and therapist.culture.lower().__contains__("collectivist")
        ):
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

    return score, matched_diagnoses, matched_specialities
