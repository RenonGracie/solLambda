import random
from zoneinfo import ZoneInfo

import pytest
from datetime import datetime, timedelta

from src.models.api.therapists import Therapist
from src.models.db.therapists import AppointmentModel
from src.utils.therapists.therapist_data_utils import provide_therapist_slots


# Fixture for current time (start of day)
@pytest.fixture
def now():
    return datetime.now(tz=ZoneInfo("US/Eastern")).replace(
        hour=7, minute=0, second=0, microsecond=0
    )


# Fixture for the therapist
@pytest.fixture
def therapist():
    return Therapist(json={"id": "", "fields": {}})


# Test 1: No assignments (empty lists)
def test_no_appointments(now):
    result = provide_therapist_slots(None, None)
    assert result == []


# Test 2: Appointments for the first week only
def test_first_week_appointments(now):
    # Create test assignments
    appointment = AppointmentModel(
        start_date=now + timedelta(hours=5),  # 12:00
        end_date=now + timedelta(hours=6, minutes=1),  # 13:01
    )
    first_week_appointments = [appointment]
    second_week_appointments = None

    result = provide_therapist_slots(
        first_week_appointments, second_week_appointments
    )

    # We check that the slot from 12:00 to 12:01 is excluded
    assert (now + timedelta(hours=5)) not in result
    assert (now + timedelta(hours=6)) not in result
    assert (
        now + timedelta(hours=4)
    ) in result  # Slot before appointment
    assert (
        now + timedelta(hours=7)
    ) in result  # Slot after appointment


# Test 3: Appointments for the second week only
def test_second_week_appointments(now):
    # Create test assignments
    appointment = AppointmentModel(
        start_date=now + timedelta(days=7, hours=10),  # 17:00 in a week
        end_date=now + timedelta(days=7, hours=11, minutes=1),  # 18:01 in a week
    )
    first_week_appointments = None
    second_week_appointments = [appointment]

    result = provide_therapist_slots(
        first_week_appointments, second_week_appointments
    )

    # We check that the slot from 17:00 to 18:01 is excluded
    assert (now + timedelta(days=7, hours=10)) not in result
    assert (now + timedelta(days=7, hours=11)) not in result
    assert (
        now + timedelta(days=7, hours=9)
    ) in result  # Slot before appointment
    assert (
        now + timedelta(days=7, hours=12)
    ) in result  # Slot after appointment


# Test 4: Appointments for both weeks
def test_both_weeks_appointments(now):
    # Create test assignments
    first_week_appointment = AppointmentModel(
        start_date=now + timedelta(hours=3),  # 10:00
        end_date=now + timedelta(hours=4, minutes=1),  # 11:01
    )
    second_week_appointment = AppointmentModel(
        start_date=now + timedelta(days=7, hours=10),  # 17:00 in a week
        end_date=now + timedelta(days=7, hours=11, minutes=1),  # 18:01 in a week
    )
    first_week_appointments = [first_week_appointment]
    second_week_appointments = [second_week_appointment]

    result = provide_therapist_slots(
        first_week_appointments, second_week_appointments
    )

    # Check that slots are excluded
    assert (now + timedelta(hours=3)) not in result
    assert (now + timedelta(hours=4)) not in result
    assert (now + timedelta(days=7, hours=10)) not in result
    assert (now + timedelta(days=7, hours=11)) not in result

    # Checking that other slots are available
    assert (now + timedelta(hours=2)) in result
    assert (now + timedelta(hours=5)) in result
    assert (now + timedelta(days=7, hours=9)) in result
    assert (now + timedelta(days=7, hours=12)) in result


# Test 5: Random Number of Occupied Slots
def test_random_booked_slots(now):
    # We generate a random number of occupied slots in the first and second weeks
    first_week_booked_slots = set(
        random.sample(range(15 * 7), random.randint(1, 15 * 7 - 1))
    )  # from 1 to 104 slots occupied (15 hours * 7 days)
    second_week_booked_slots = set(
        random.sample(range(15 * 7), random.randint(1, 15 * 7 - 1))
    )  # from 1 to 104 slots occupied (15 hours * 7 days)

    # Create test assignments for the first week
    first_week_appointments = [
        AppointmentModel(
            start_date=now + timedelta(hours=slot),
            end_date=now + timedelta(hours=slot + 1),
        )
        for slot in first_week_booked_slots
    ]

    # Create test assignments for the second week
    second_week_appointments = [
        AppointmentModel(
            start_date=now + timedelta(days=7, hours=slot),
            end_date=now + timedelta(days=7, hours=slot + 1),
        )
        for slot in second_week_booked_slots
    ]

    # Calling the method
    result = provide_therapist_slots(
        first_week_appointments, second_week_appointments
    )

    # Check that occupied slots are excluded
    for slot in first_week_booked_slots:
        assert (now + timedelta(hours=slot)) not in result

    for slot in second_week_booked_slots:
        assert (now + timedelta(days=7, hours=slot)) not in result
