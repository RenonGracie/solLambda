from datetime import datetime

from googleapiclient.errors import HttpError


from googleapiclient.discovery import build

from src.utils.constants.contants import DATE_FORMAT
from src.utils.google.credentials import get_credentials
from src.utils.logger import get_logger

logger = get_logger()


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
        logger.error(
            "Fetch calendar error", extra={"calendar_id": calendar_id, "error": str(e)}
        )
        if raise_error:
            raise e
        return []
    finally:
        service.close()


def get_busy_events_from_gcalendar(
    calendar_ids: list[str],
    time_min: datetime | str | None = None,
    time_max: datetime | str | None = None,
    raise_error: bool = False,
) -> dict | None:
    """
    Get busy periods for specified calendars using Google Calendar freebusy API.

    Args:
        calendar_ids: List of calendar IDs to check
        time_min: Start time in format (e.g., '2024-03-20')
        time_max: End time in format (e.g., '2024-03-21')
        raise_error: Whether to raise exceptions or return None on error

    Returns:
        Dictionary containing busy periods for each calendar
    """
    if isinstance(time_min, datetime):
        time_min = time_min.strftime(DATE_FORMAT)

    if isinstance(time_max, datetime):
        time_max = time_max.strftime(DATE_FORMAT)

    service = _get_service()
    try:
        # Prepare request body for freebusy query
        body = {
            "timeMin": f"{time_min}T00:00:00+0000",
            "timeMax": f"{time_max}T23:59:59+0000",
            "items": [{"id": calendar_id} for calendar_id in calendar_ids],
        }

        # Execute freebusy query
        result = service.freebusy().query(body=body).execute()
        return result.get("calendars", {})

    except HttpError as e:
        logger.error(
            "Freebusy query error",
            extra={"calendar_ids": calendar_ids, "error": str(e)},
        )
        if raise_error:
            raise e
        return None
    finally:
        service.close()
