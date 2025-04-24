from datetime import datetime, timedelta

from src.utils.constants.contants import DEFAULT_ZONE
from src.utils.matching_algorithm.match import provide_therapist_slots


def check_therapist_availability(slot: datetime, busy_slots: list[dict]) -> str | None:
    """
    Checks therapist availability for the specified time slot.

    Args:
        slot: Time slot to check
        busy_slots: List of dictionaries with information about existing appointments

    Returns:
        None if the slot is available, otherwise a string with the reason for unavailability
    """
    next_day = datetime.now().astimezone(DEFAULT_ZONE) + timedelta(days=1)
    slot = slot.astimezone(DEFAULT_ZONE)

    if slot < next_day:
        return "You cannot book an appointment less than 24 hours in advance."

    if 7 <= slot.hour < 22:
        slots = provide_therapist_slots([slot], busy_slots)
        if len(slots) == 0:
            return "This time slot is already taken."
        return None
    else:
        return "You can't book an appointment outside of working hours."
