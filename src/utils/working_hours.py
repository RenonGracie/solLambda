from datetime import datetime, timedelta

from src.utils.constants.contants import DEFAULT_ZONE


def current_working_hours() -> (datetime, int):
    return datetime.now(tz=DEFAULT_ZONE).replace(
        hour=7, minute=0, second=0, microsecond=0
    ), 16


def week_slots(
    day_start: datetime | None = None, hours_count: int | None = None
) -> list:
    first_week_slots = []
    second_week_slots = []

    if not day_start or not hours_count:
        start, count = current_working_hours()
        day_start = day_start or start
        hours_count = hours_count or count

    for day in range(7):
        for hour in range(hours_count):
            first_week_slots.append(day_start + timedelta(hours=hour, days=day))
            second_week_slots.append(day_start + timedelta(hours=hour, days=day + 7))

    return first_week_slots + second_week_slots
