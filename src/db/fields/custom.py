from datetime import datetime

from sqlalchemy import TypeDecorator, String
from dateutil.parser import parse


class DateTimeAsString(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, length=32, *args, **kwargs):
        super().__init__(length=length, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, str):
            parse(value)
            return value
        raise ValueError("Expected datetime or string, got {}".format(type(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return parse(value)
