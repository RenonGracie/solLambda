import json

import pytest

from src.models.db.airtable import AirtableTherapist
from src.models.db.signup_form import ClientSignup
from src.utils.matching_algorithm.algorithm import calculate_match_score


@pytest.fixture
def sample_therapist():
    therapist = AirtableTherapist()
    therapist.states = ["CA", "NY"]
    therapist.accepting_new_clients = True
    therapist.gender = "Male"
    therapist.experience_with_risk_clients = "Yes, no"
    therapist.diagnoses = ["Anxiety", "Depression"]
    therapist.specialities = ["Trauma", "Family Therapy"]
    therapist.traditional_vs_non_traditional_family_household = "Non-traditional"
    therapist.individualist_vs_collectivist_culture = "Individualist"
    therapist.many_places_or_only_one_or_two_places = "Many places"
    therapist.lgbtq_part = True
    therapist.negative_affect_by_social_media = False
    return therapist


@pytest.fixture
def sample_client():
    return ClientSignup(
        response_id="1",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        gender="Male",
        age="25",
        state="California",
        _therapist_specializes_in=json.dumps(["Is male", "Trauma", "Family Therapy"]),
        therapist_identifies_as="Male",
        pleasure_doing_things="Nearly every day",
        feeling_down="Several days",
        trouble_falling="More than half the days",
        feeling_tired="Not at all",
        poor_appetite="Not at all",
        feeling_bad_about_yourself="Several days",
        trouble_concentrating="More than half the days",
        moving_or_speaking_so_slowly="Not at all",
        suicidal_thoughts="Not at all",
        feeling_nervous="More than half the days",
        not_control_worrying="Nearly every day",
        worrying_too_much="More than half the days",
        trouble_relaxing="Several days",
        being_so_restless="Several days",
        easily_annoyed="Not at all",
        feeling_afraid="Not at all",
        university="Some University",
        _lived_experiences=json.dumps(
            ["Non-traditional", "Individualist", "Many places"]
        ),
        _how_did_you_hear_about_us=json.dumps(["Google"]),
    )


# Test cases
def test_hard_factor_state_mismatch(sample_client, sample_therapist):
    sample_client.state = "TX"
    score, matched_diagnoses_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses_specialities == []


def test_hard_factor_gender_mismatch(sample_client, sample_therapist):
    sample_client.therapist_identifies_as = ["Female"]
    score, matched_diagnoses_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses_specialities == []


def test_ph9_hard_factor(sample_client, sample_therapist):
    sample_client.pleasure_doing_things = "Nearly every day"
    sample_client.feeling_down = "Nearly every day"
    sample_client.trouble_falling = "Nearly every day"
    sample_client.feeling_tired = "Nearly every day"
    sample_client.poor_appetite = "Nearly every day"
    sample_client.feeling_bad_about_yourself = "Nearly every day"
    sample_client.trouble_concentrating = "Nearly every day"
    sample_client.moving_or_speaking_so_slowly = "Nearly every day"

    score, matched_diagnoses_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses_specialities == []


def test_no_matches(sample_client, sample_therapist):
    sample_client.therapist_specializes_in = []
    sample_client.therapist_identifies_as = "Female"
    sample_client.lived_experiences = []
    score, matched_diagnoses_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses_specialities == []


def test_calculate_match_score_full_match(sample_client, sample_therapist):
    sample_client.lived_experiences = [
        "Non-traditional family",
        "Gen immigrant",
        "Individualist",
        "Many places",
        "Caretaker role",
        "Affected by social media",
    ]
    sample_client.therapist_specializes_in = [
        "Anxiety",
        "CBT",
        "DBT",
        "Trauma",
        "Depression",
    ]
    sample_client.therapist_identifies_as = "Male"
    sample_therapist.diagnoses_specialities = ["Anxiety", "Depression", "Trauma"]
    sample_therapist.therapeutic_orientation = ["CBT", "DBT"]
    score, matched_diagnoses_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == 15  # Adjust based on your scoring logic
    assert "Anxiety" in matched_diagnoses_specialities
    assert "Trauma" in matched_diagnoses_specialities
