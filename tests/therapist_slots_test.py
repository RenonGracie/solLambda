import random

import pytest
from datetime import datetime, timedelta

from src.models.api.therapists import Therapist
from src.utils.matching_algorithm.match import provide_therapist_slots
from src.utils.working_hours import current_working_hours, week_slots


# Fixture for current time (start of day)
@pytest.fixture
def now():
    return current_working_hours()


# Fixture for current time (start of day)
@pytest.fixture
def slots(now):
    day_start, hours_count = now
    return week_slots(day_start, hours_count)


# Fixture for the therapist
@pytest.fixture
def therapist():
    return Therapist(json={"id": "", "fields": {}})


# Test 1: No busy slots
def test_no_busy_slots(now, slots):
    result = provide_therapist_slots(slots, [])
    assert result == slots


# Test 2: Single busy slot in first week
def test_single_busy_slot_first_week(now, slots):
    day_start, hours_count = now

    # Create test busy slot
    busy_slot = {
        "start": (day_start + timedelta(hours=5)).isoformat(),  # 12:00
        "end": (day_start + timedelta(hours=6, minutes=1)).isoformat(),  # 13:01
    }

    result = provide_therapist_slots(slots, [busy_slot])

    # Check that slots during busy period are excluded
    assert (day_start + timedelta(hours=5)) not in result
    assert (day_start + timedelta(hours=6)) not in result
    assert (day_start + timedelta(hours=4)) in result  # Slot before busy period
    assert (day_start + timedelta(hours=7)) in result  # Slot after busy period


# Test 3: Single busy slot in second week
def test_single_busy_slot_second_week(now, slots):
    day_start, hours_count = now

    # Create test busy slot
    busy_slot = {
        "start": (
            day_start + timedelta(days=7, hours=10)
        ).isoformat(),  # 17:00 in a week
        "end": (
            day_start + timedelta(days=7, hours=11, minutes=1)
        ).isoformat(),  # 18:01 in a week
    }

    result = provide_therapist_slots(slots, [busy_slot])

    # Check that slots during busy period are excluded
    assert (day_start + timedelta(days=7, hours=10)) not in result
    assert (day_start + timedelta(days=7, hours=11)) not in result
    assert (day_start + timedelta(days=7, hours=9)) in result  # Slot before busy period
    assert (day_start + timedelta(days=7, hours=12)) in result  # Slot after busy period


# Test 4: Multiple busy slots in both weeks
def test_multiple_busy_slots(now, slots):
    day_start, hours_count = now

    # Create test busy slots
    busy_slots = [
        {
            "start": (day_start + timedelta(hours=3)).isoformat(),  # 10:00
            "end": (day_start + timedelta(hours=4, minutes=1)).isoformat(),  # 11:01
        },
        {
            "start": (
                day_start + timedelta(days=7, hours=10)
            ).isoformat(),  # 17:00 in a week
            "end": (
                day_start + timedelta(days=7, hours=11, minutes=1)
            ).isoformat(),  # 18:01 in a week
        },
    ]

    result = provide_therapist_slots(slots, busy_slots)

    # Check that slots during busy periods are excluded
    assert (day_start + timedelta(hours=3)) not in result
    assert (day_start + timedelta(hours=4)) not in result
    assert (day_start + timedelta(days=7, hours=10)) not in result
    assert (day_start + timedelta(days=7, hours=11)) not in result

    # Check that other slots are available
    assert (day_start + timedelta(hours=2)) in result
    assert (day_start + timedelta(hours=5)) in result
    assert (day_start + timedelta(days=7, hours=9)) in result
    assert (day_start + timedelta(days=7, hours=12)) in result


# Test 5: Random busy slots
def test_random_busy_slots(now, slots):
    day_start, hours_count = now

    # Generate random busy slots
    num_busy_slots = random.randint(1, 10)
    busy_slots = []
    for _ in range(num_busy_slots):
        # Randomly choose between first and second week
        week_offset = random.choice([0, 7])
        hour = random.randint(0, 14)
        busy_slots.append(
            {
                "start": (
                    day_start + timedelta(days=week_offset, hours=hour)
                ).isoformat(),
                "end": (
                    day_start + timedelta(days=week_offset, hours=hour + 1)
                ).isoformat(),
            }
        )

    result = provide_therapist_slots(slots, busy_slots)

    # Check that all busy slots are excluded
    for busy_slot in busy_slots:
        start_time = datetime.fromisoformat(busy_slot["start"])
        end_time = datetime.fromisoformat(busy_slot["end"])
        for slot in slots:
            if start_time <= slot < end_time:
                assert slot not in result


# Test 6: Working hours
def test_working_hours(now, slots):
    day_start, hours_count = now

    assert day_start.replace(hour=22) in slots
    assert day_start.replace(hour=7) in slots

    assert day_start.replace(hour=6) not in slots
    assert day_start.replace(hour=23) not in slots
