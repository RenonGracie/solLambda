import json
from datetime import datetime

from pyairtable import Api

from src.utils.google_calendar import get_events_from_gcalendar
from src.utils.settings import settings

api = Api(settings.AIRTABLE_API_KEY)
table = api.table(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_ID)


def _filter_event(event):
    filtered_event = {}
    for key in ["start", "end", "description", "recurrence"]:
        if key in event:
            filtered_event[key] = event[key]
    return filtered_event


def main():
    print("started")
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone()
    now_str = f"{now.strftime("%Y-%m-%d")}T00:00:00-00:00"
    print(now_str)

    data = []
    for value in table.all():
        email = value["fields"].get("Email") or value["fields"].get("Notes")
        print("Working on", email)
        if email:
            events = get_events_from_gcalendar(email, time_min=now_str)
            if events:
                data.append(
                    {
                        "name": value["fields"].get("Name")
                        or value["fields"].get("Intern Name"),
                        "email": email,
                        "events": [_filter_event(event) for event in events],
                    }
                )
    print("Writing to file")
    with open("events.json", "w") as f:
        f.write(json.dumps({"therapists": data}))
    print("finished")


if __name__ == "__main__":
    main()
