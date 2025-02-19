import pytest

from src.models.api.therapists import Therapist
from src.utils.therapist_data_utils import implement_age_factor


# Fixture for creating test data
@pytest.fixture
def sample_therapists():
    return [
        {"therapist": Therapist(json={"id": "", "fields": {"Age": "Early/Mid 20s"}})},
        {"therapist": Therapist(json={"id": "", "fields": {"Age": "Late 20s"}})},
        {"therapist": Therapist(json={"id": "", "fields": {"Age": "30s"}})},
        {"therapist": Therapist(json={"id": "", "fields": {"Age": "30s"}})},
        {"therapist": Therapist(json={"id": "", "fields": {"Age": "40s"}})},
        {"therapist": Therapist(json={"id": "", "fields": {"Age": "60+"}})},
    ]


# Tests for implement_age_factor
def test_implement_age_factor_valid_age(sample_therapists):
    age_str = "35"
    result = implement_age_factor(age_str, sample_therapists)
    # We expect therapists in the "30s" age group to be at the start
    assert result[0]["therapist"].age == "30s"
    assert len(result) == len(
        sample_therapists
    )  # The length of the list should not change.


def test_implement_age_factor_limit_to_3(sample_therapists):
    age_str = "30"
    # Let's add more therapists with age group "30s"
    sample_therapists.extend(
        [
            {"therapist": Therapist(json={"id": "", "fields": {"Age": "30s"}})},
            {"therapist": Therapist(json={"id": "", "fields": {"Age": "30s"}})},
        ]
    )
    result = implement_age_factor(age_str, sample_therapists)
    # We expect that only 3 therapists with the "30s" group will be at the beginning
    assert result[0]["therapist"].age == "30s"
    assert result[1]["therapist"].age == "30s"
    assert result[2]["therapist"].age == "30s"
    assert len(result) == len(
        sample_therapists
    )  # The length of the list should not change.


def test_implement_age_factor_invalid_age(sample_therapists):
    age_str = "not_a_number"
    result = implement_age_factor(age_str, sample_therapists)
    # We expect the list to remain unchanged.
    assert result == sample_therapists


def test_implement_age_factor_empty_list():
    age_str = "30"
    result = implement_age_factor(age_str, [])
    # Expecting an empty list
    assert result == []
