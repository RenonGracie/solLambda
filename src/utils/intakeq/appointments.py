from datetime import datetime, timedelta, UTC

from src.utils.constants.contants import DEFAULT_ZONE


def check_therapist_availability(
    slot: datetime, appointments: list[dict]
) -> (dict | None, str | None):
    """
    Checks therapist availability for the specified time slot.

    Args:
        slot: Time slot to check
        appointments: List of dictionaries with information about existing appointments

    Returns:
        None if the slot is available, otherwise a string with the reason for unavailability
    """
    next_day = datetime.now().astimezone() + timedelta(days=1)
    slot = slot.astimezone(DEFAULT_ZONE)

    if slot < next_day:
        return None, "You cannot book an appointment less than 24 hours in advance."

    if 7 <= slot.hour < 22:
        for data in appointments:
            start_date = datetime.fromtimestamp(
                data["StartDate"] / 1e3, UTC
            ).astimezone()
            end_date = datetime.fromtimestamp(data["EndDate"] / 1e3, UTC).astimezone()
            if start_date <= slot < end_date:
                return data, "This time slot is already taken."
        return None, None
    else:
        return None, "You can't book an appointment outside of working hours."
