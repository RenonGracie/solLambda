from datetime import datetime
from time import sleep

import requests
from pyairtable import Api

from src.utils.google.google_calendar import get_events_from_gcalendar
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

    for value in table.all():
        name = value["fields"].get("Name") or value["fields"].get("Intern Name")
        email = value["fields"].get("Email") or value["fields"].get("Notes")
        calendar_email = value["fields"].get("Calendar") or email
        print("Working on", name, calendar_email)
        if calendar_email:
            events = get_events_from_gcalendar(calendar_email, time_min=now_str)
            if len(events) > 0:
                therapist_data = {
                    "name": name,
                    "email": email,
                    "calendar_email": calendar_email,
                    "events": [_filter_event(event) for event in events],
                }
                print("Sending data", calendar_email)
                result = requests.post(
                    url=f"fhttps://api.therapists.solhealth.co/therapists/set_events?admin_password={settings.ADMIN_PASSWORD}",
                    json={"therapist": therapist_data},
                )
                print(result)
            else:
                print("List events is empty", calendar_email)
        sleep(1)
    print("finished")


if __name__ == "__main__":
    main()
