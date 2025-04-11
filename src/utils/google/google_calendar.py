from googleapiclient.errors import HttpError


from googleapiclient.discovery import build

from src.utils.google.credentials import get_credentials


def _get_service():
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


def insert_email_to_gcalendar(calendar_id: str) -> None:
    service = _get_service()
    try:
        service.calendarList().insert(body={"id": calendar_id}).execute()
    finally:
        service.close()


def gcalendar_list():
    service = _get_service()
    try:
        page_token = None
        data = []
        while True:
            calendars = service.calendarList().list(pageToken=page_token).execute()
            data += calendars["items"]
            page_token = calendars.get("nextPageToken")
            if not page_token:
                break
        return data
    except HttpError:
        return []
    finally:
        service.close()


def get_events_from_gcalendar(
    calendar_id: str,
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 1000,
    raise_error: bool = False,
) -> list[dict] | None:
    service = _get_service()
    try:
        insert_email_to_gcalendar(calendar_id)
        page_token = None
        data = []
        while True:
            events = (
                service.events()
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
    except HttpError as e:
        print("Fetch calendar error", calendar_id, str(e))
        if raise_error:
            raise e
        return []
    finally:
        service.close()
