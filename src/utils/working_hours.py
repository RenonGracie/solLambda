from datetime import datetime

from src.utils.constants.contants import DEFAULT_ZONE


def current_working_hours() -> (datetime, int):
    return datetime.now(tz=DEFAULT_ZONE).replace(
        hour=7, minute=0, second=0, microsecond=0
    ), 15
