from datetime import datetime, timedelta
from unittest.mock import patch

from src.utils.constants.contants import DEFAULT_ZONE
from src.utils.intakeq.appointments import check_therapist_availability


def test_check_therapist_availability_less_than_24_hours():
    """Test that booking less than 24 hours in advance is rejected"""
    # Create a slot for today (less than 24 hours from now)
    today = datetime.now(DEFAULT_ZONE)
    slot = today.replace(hour=14, minute=0, second=0, microsecond=0).astimezone(
        DEFAULT_ZONE
    )

    # Mock current time to be just before the slot
    mock_now = slot - timedelta(hours=1)

    with patch("src.utils.intakeq.appointments.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        result = check_therapist_availability(slot, [])
        assert result == "You cannot book an appointment less than 24 hours in advance."


def test_check_therapist_availability_more_than_24_hours():
    """Test that booking more than 24 hours in advance is allowed if no conflicts"""
    # Create a slot for tomorrow (more than 24 hours from now)
    tomorrow = datetime.now(DEFAULT_ZONE) + timedelta(
        days=2
    )  # Two days ahead to ensure it's more than 24 hours
    slot = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0).astimezone(
        DEFAULT_ZONE
    )

    # Mock current time to be more than 24 hours before the slot
    mock_now = slot - timedelta(days=2)

    with patch("src.utils.intakeq.appointments.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        result = check_therapist_availability(slot, [])
        assert result is None


def test_check_therapist_availability_outside_working_hours():
    """Test that booking outside working hours (before 7 AM or after 10 PM) is rejected"""
    # Create a slot for tomorrow at 6 AM (outside working hours)
    tomorrow = datetime.now(DEFAULT_ZONE) + timedelta(
        days=2
    )  # Two days ahead to ensure it's more than 24 hours
    early_slot = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0)

    # Create a slot for tomorrow at 10 PM (outside working hours)
    late_slot = tomorrow.replace(hour=22, minute=0, second=0, microsecond=0)

    # Mock current time to be more than 24 hours before the slots
    mock_now = early_slot - timedelta(days=2)

    with patch("src.utils.intakeq.appointments.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        # Test early slot (6 AM)
        result = check_therapist_availability(early_slot, [])
        assert result == "You can't book an appointment outside of working hours."

        # Test late slot (10 PM)
        result = check_therapist_availability(late_slot, [])
        assert result == "You can't book an appointment outside of working hours."


def test_check_therapist_availability_conflict():
    """Test that booking during an existing appointment is rejected"""
    # Create a slot for tomorrow at 10:30 AM
    tomorrow = datetime.now(DEFAULT_ZONE) + timedelta(
        days=2
    )  # Two days ahead to ensure it's more than 24 hours
    slot = tomorrow.replace(hour=10, minute=30, second=0, microsecond=0).astimezone(
        DEFAULT_ZONE
    )

    # Create an existing appointment from 10:00 AM to 11:00 AM
    start_time = tomorrow.replace(
        hour=10, minute=0, second=0, microsecond=0
    ).astimezone(DEFAULT_ZONE)
    end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0).astimezone(
        DEFAULT_ZONE
    )

    appointments = [
        {
            "StartDate": int(start_time.timestamp() * 1000),
            "EndDate": int(end_time.timestamp() * 1000),
        }
    ]

    # Mock current time to be more than 24 hours before the slot
    mock_now = slot - timedelta(days=2)

    with patch("src.utils.intakeq.appointments.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        result = check_therapist_availability(slot, appointments)
        assert result == "This time slot is already taken."


def test_check_therapist_availability_no_conflict():
    """Test that booking during working hours with no conflicts is allowed"""
    # Create a slot for tomorrow at 2:00 PM
    tomorrow = datetime.now(DEFAULT_ZONE) + timedelta(
        days=2
    )  # Two days ahead to ensure it's more than 24 hours
    slot = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0).astimezone(
        DEFAULT_ZONE
    )

    # Create an existing appointment from 10:00 AM to 11:00 AM
    start_time = tomorrow.replace(
        hour=10, minute=0, second=0, microsecond=0
    ).astimezone(DEFAULT_ZONE)
    end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0).astimezone(
        DEFAULT_ZONE
    )

    appointments = [
        {
            "StartDate": int(start_time.timestamp() * 1000),
            "EndDate": int(end_time.timestamp() * 1000),
        }
    ]

    # Mock current time to be more than 24 hours before the slot
    mock_now = slot - timedelta(days=2)

    with patch("src.utils.intakeq.appointments.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        result = check_therapist_availability(slot, appointments)
        assert result is None
