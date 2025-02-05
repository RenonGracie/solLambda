import base64
import json

from src.utils.settings import settings

from google.oauth2 import service_account
from googleapiclient.discovery import build

__SCOPES = ["https://www.googleapis.com/auth/calendar"]

__creds_json = json.loads(
    base64.b64decode(settings.GOOGLE_CALENDAR_CREDENTIALS).decode()
)
__creds = service_account.Credentials.from_service_account_info(
    __creds_json, scopes=__SCOPES
)
__service = build("calendar", "v3", credentials=__creds)


def get_events_from_gcalendar(
    calendar_id: str,
    time_min: str | None,
    time_max: str | None,
    max_results: int | None,
) -> list[dict]:
    __service.calendarList().insert(body={"id": calendar_id}).execute()
    page_token = None
    data = []
    while True:
        events = (
            __service.events()
            .list(
                calendarId=calendar_id,
                pageToken=page_token,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
            )
            .execute()
        )
        data.append(events["items"])
        page_token = events.get("nextPageToken")
        if not page_token:
            break
    return data
