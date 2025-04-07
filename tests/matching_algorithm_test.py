import json

import pytest

from src.models.api.therapists import Therapist
from src.models.db.signup_form import ClientSignup
from src.utils.matching_algorithm.algorithm import calculate_match_score


@pytest.fixture
def sample_therapist():
    return Therapist(
        {
            "id": "1",
            "fields": {
                "States": ["CA", "NY"],
                "Accepting New Clients": "Yes",
                "Gender": "Male",
                "Experience and/or interest in working with higher-risk clients": "Yes",
                "Diagnoses: Please select the diagnoses you have experience and/or interest in working with": [
                    "Anxiety",
                    "Depression",
                ],
                "Specialities: Please select any specialities you have experience and/or interest in working with. ": [
                    "Trauma",
                    "Family Therapy",
                ],
                "Traditional vs. Non-traditional family household": "Non-traditional",
                "Individualist vs. Collectivist culture": "Individualist",
                "Many places or only one or two places?": "Many places",
                "LGBTQ+: Are you a part of the LGBTQ+ community?": "Yes",
                "Social Media: Have you ever been negatively affected by social media?": "No",
            },
        }
    )


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
        state="CA",
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
    score, matched_diagnoses, matched_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses == []
    assert matched_specialities == []


def test_hard_factor_gender_mismatch(sample_client, sample_therapist):
    sample_client.therapist_identifies_as = ["Female"]
    score, matched_diagnoses, matched_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses == []
    assert matched_specialities == []


def test_ph9_hard_factor(sample_client, sample_therapist):
    sample_client.pleasure_doing_things = "Nearly every day"
    sample_client.feeling_down = "Nearly every day"
    sample_client.trouble_falling = "Nearly every day"
    sample_client.feeling_tired = "Nearly every day"
    sample_client.poor_appetite = "Nearly every day"
    sample_client.feeling_bad_about_yourself = "Nearly every day"
    sample_client.trouble_concentrating = "Nearly every day"
    sample_client.moving_or_speaking_so_slowly = "Nearly every day"

    score, matched_diagnoses, matched_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses == []
    assert matched_specialities == []


def test_soft_factors(sample_client, sample_therapist):
    score, matched_diagnoses, matched_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == 12
    assert "Trauma" in matched_specialities
    assert "Family Therapy" in matched_specialities


def test_no_matches(sample_client, sample_therapist):
    sample_client.therapist_specializes_in = []
    sample_client.therapist_identifies_as = "Female"
    sample_client.lived_experiences = []
    score, matched_diagnoses, matched_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == -1
    assert matched_diagnoses == []
    assert matched_specialities == []


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
        "CBT-focused",
        "DBT skills based",
        "Trauma",
    ]
    sample_client.therapist_identifies_as = "Male"
    sample_therapist.diagnoses = ["Anxiety", "Depression"]
    sample_therapist.specialities = ["Trauma"]
    sample_therapist.therapeutic_orientation = ["CBT", "DBT"]
    score, matched_diagnoses, matched_specialities = calculate_match_score(
        sample_client, sample_therapist
    )
    assert score == 18  # Adjust based on your scoring logic
    assert "Anxiety" in matched_diagnoses
    assert "Trauma" in matched_specialities
