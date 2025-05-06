import random

import pytest
from datetime import datetime, timedelta

from src.models.api.therapists import Therapist
from src.utils.matching_algorithm.match import provide_therapist_slots
from src.utils.working_hours import current_working_hours


# Fixture for current time (start of day)
@pytest.fixture
def now():
    day_start, hours_count = current_working_hours()
    return day_start


# Fixture for current time (start of day)
@pytest.fixture
def slots(now):
    first_week_slots = []
    second_week_slots = []
    for day in range(7):
        for hour in range(15):
            first_week_slots.append(now + timedelta(hours=hour, days=day))
            second_week_slots.append(now + timedelta(hours=hour, days=day + 7))
    return first_week_slots, second_week_slots


# Fixture for the therapist
@pytest.fixture
def therapist():
    return Therapist(json={"id": "", "fields": {}})


# Test 1: No busy slots
def test_no_busy_slots(now, slots):
    first_week_slots, second_week_slots = slots
    all_slots = first_week_slots + second_week_slots
    result = provide_therapist_slots(all_slots, [])
    assert result == all_slots


# Test 2: Single busy slot in first week
def test_single_busy_slot_first_week(now, slots):
    first_week_slots, second_week_slots = slots
    all_slots = first_week_slots + second_week_slots

    # Create test busy slot
    busy_slot = {
        "start": (now + timedelta(hours=5)).isoformat(),  # 12:00
        "end": (now + timedelta(hours=6, minutes=1)).isoformat(),  # 13:01
    }

    result = provide_therapist_slots(all_slots, [busy_slot])

    # Check that slots during busy period are excluded
    assert (now + timedelta(hours=5)) not in result
    assert (now + timedelta(hours=6)) not in result
    assert (now + timedelta(hours=4)) in result  # Slot before busy period
    assert (now + timedelta(hours=7)) in result  # Slot after busy period


# Test 3: Single busy slot in second week
def test_single_busy_slot_second_week(now, slots):
    first_week_slots, second_week_slots = slots
    all_slots = first_week_slots + second_week_slots

    # Create test busy slot
    busy_slot = {
        "start": (now + timedelta(days=7, hours=10)).isoformat(),  # 17:00 in a week
        "end": (
            now + timedelta(days=7, hours=11, minutes=1)
        ).isoformat(),  # 18:01 in a week
    }

    result = provide_therapist_slots(all_slots, [busy_slot])

    # Check that slots during busy period are excluded
    assert (now + timedelta(days=7, hours=10)) not in result
    assert (now + timedelta(days=7, hours=11)) not in result
    assert (now + timedelta(days=7, hours=9)) in result  # Slot before busy period
    assert (now + timedelta(days=7, hours=12)) in result  # Slot after busy period


# Test 4: Multiple busy slots in both weeks
def test_multiple_busy_slots(now, slots):
    first_week_slots, second_week_slots = slots
    all_slots = first_week_slots + second_week_slots

    # Create test busy slots
    busy_slots = [
        {
            "start": (now + timedelta(hours=3)).isoformat(),  # 10:00
            "end": (now + timedelta(hours=4, minutes=1)).isoformat(),  # 11:01
        },
        {
            "start": (now + timedelta(days=7, hours=10)).isoformat(),  # 17:00 in a week
            "end": (
                now + timedelta(days=7, hours=11, minutes=1)
            ).isoformat(),  # 18:01 in a week
        },
    ]

    result = provide_therapist_slots(all_slots, busy_slots)

    # Check that slots during busy periods are excluded
    assert (now + timedelta(hours=3)) not in result
    assert (now + timedelta(hours=4)) not in result
    assert (now + timedelta(days=7, hours=10)) not in result
    assert (now + timedelta(days=7, hours=11)) not in result

    # Check that other slots are available
    assert (now + timedelta(hours=2)) in result
    assert (now + timedelta(hours=5)) in result
    assert (now + timedelta(days=7, hours=9)) in result
    assert (now + timedelta(days=7, hours=12)) in result


# Test 5: Random busy slots
def test_random_busy_slots(now, slots):
    first_week_slots, second_week_slots = slots
    all_slots = first_week_slots + second_week_slots

    # Generate random busy slots
    num_busy_slots = random.randint(1, 10)
    busy_slots = []
    for _ in range(num_busy_slots):
        # Randomly choose between first and second week
        week_offset = random.choice([0, 7])
        hour = random.randint(0, 14)
        busy_slots.append(
            {
                "start": (now + timedelta(days=week_offset, hours=hour)).isoformat(),
                "end": (now + timedelta(days=week_offset, hours=hour + 1)).isoformat(),
            }
        )

    result = provide_therapist_slots(all_slots, busy_slots)

    # Check that all busy slots are excluded
    for busy_slot in busy_slots:
        start_time = datetime.fromisoformat(busy_slot["start"])
        end_time = datetime.fromisoformat(busy_slot["end"])
        for slot in all_slots:
            if start_time <= slot < end_time:
                assert slot not in result
