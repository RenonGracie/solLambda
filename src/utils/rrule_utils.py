from datetime import timedelta


def get_start_date(start_date, rrule_str: str):
    if not rrule_str.__contains__("BYDAY="):
        return start_date

    byday = rrule_str.split("BYDAY=")[1].split(";")[0]
    day_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
    target_days = [day_map[day] for day in byday.split(",")]
    current_day = start_date.weekday()

    first_days = []
    for target_day in target_days:
        days_ahead = (target_day - current_day) % 7
        first_day = start_date + timedelta(days=days_ahead)
        first_days.append(first_day)
    return min(first_days)
