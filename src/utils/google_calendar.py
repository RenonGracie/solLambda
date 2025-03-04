import base64
import json

from googleapiclient.errors import HttpError

from src.utils.settings import settings

from google.oauth2 import service_account
from googleapiclient.discovery import build

_SCOPES = ["https://www.googleapis.com/auth/calendar"]

_creds_json = json.loads(
    base64.b64decode(settings.GOOGLE_CALENDAR_CREDENTIALS).decode()
)
_creds = service_account.Credentials.from_service_account_info(
    _creds_json, scopes=_SCOPES
)
_service = build("calendar", "v3", credentials=_creds)


def insert_email_to_gcalendar(calendar_id: str) -> None:
    _service.calendarList().insert(body={"id": calendar_id}).execute()


def get_events_from_gcalendar(
    calendar_id: str,
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int | None = None,
) -> list[dict]:
    try:
        insert_email_to_gcalendar(calendar_id)
        page_token = None
        data = []
        while True:
            events = (
                _service.events()
                .list(
                    calendarId=calendar_id,
                    pageToken=page_token,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                )
                .execute()
            )
            data += events["items"]
            page_token = events.get("nextPageToken")
            if not page_token:
                break
        return data
    except HttpError:
        return []
