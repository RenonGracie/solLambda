from collections import defaultdict

from dateutil import parser


def _get_event_date(event):
    return parser.parse(
        event["start"].get("dateTime") or event["start"].get("date")
    ).strftime("%Y-%m-%d")


def _format_event(event):
    return {
        "event": event.get("summary"),
        "start": event["start"].get("dateTime") or event["start"].get("date"),
        "end": event["end"].get("dateTime") or event["end"].get("date"),
        "zone": event["end"].get("timeZone"),
        "description": event.get("description"),
        "recurrence": event.get("recurrence"),
    }


def parse_calendar_events(events: list[dict]):
    grouped_events = defaultdict(list)
    for event in events:
        if event.get("start") and event.get("end"):
            date = _get_event_date(event)
            formatted_event = _format_event(event)
            grouped_events[date].append(formatted_event)

    result = [
        {"date": date, "events": events} for date, events in grouped_events.items()
    ]

    result.sort(key=lambda x: x["date"])
    return result
