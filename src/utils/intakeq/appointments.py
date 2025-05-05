from datetime import datetime, timedelta, UTC

from src.utils.constants.contants import DEFAULT_ZONE
from src.utils.matching_algorithm.match import provide_therapist_slots


def check_therapist_availability(
    slot: datetime, slots: list[dict], is_appointments: bool = False
) -> str | None:
    """
    Checks therapist availability for the specified time slot.

    Args:
        slot: Time slot to check
        slots: List of dictionaries with information about existing appointments
        is_appointments: If the list of events is from intakeQ

    Returns:
        None if the slot is available, otherwise a string with the reason for unavailability
    """
    next_day = datetime.now().astimezone(DEFAULT_ZONE) + timedelta(days=1)
    slot = slot.astimezone(DEFAULT_ZONE)

    if slot < next_day:
        return "You cannot book an appointment less than 24 hours in advance."

    if 7 <= slot.hour < 22:
        if is_appointments:
            for data in slots:
                start_date = datetime.fromtimestamp(
                    data["StartDate"] / 1e3, UTC
                ).astimezone()
                end_date = datetime.fromtimestamp(
                    data["EndDate"] / 1e3, UTC
                ).astimezone()
                if start_date <= slot < end_date:
                    return "This time slot is already taken."
        else:
            slots = provide_therapist_slots([slot], slots)
            if len(slots) == 0:
                return "This time slot is already taken."
        return None
    else:
        return "You can't book an appointment outside of working hours."
