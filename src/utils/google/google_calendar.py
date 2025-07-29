from datetime import UTC, datetime, timedelta

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils.constants.contants import DATE_FORMAT
from src.utils.google.credentials import get_credentials
from src.utils.logger import get_logger
from src.utils.settings import settings

logger = get_logger()


def _get_service(subject_email: str | None = None):
    creds = get_credentials()
    if subject_email:
        creds = creds.with_subject(subject_email)
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
    service = _get_service(
        settings.CONTACT_EMAIL if calendar_id.endswith("@solhealth.co") else None
    )
    try:
        if not calendar_id.endswith("@solhealth.co"):
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

    def _fetch_busy_events(ids: list[str], use_solhealth: bool = False) -> dict | None:
        service = _get_service(settings.CONTACT_EMAIL if use_solhealth else None)
        try:
            # Prepare request body for freebusy query
            body = {
                "timeMin": f"{time_min}T00:00:00+0000",
                "timeMax": f"{time_max}T23:59:59+0000",
                "items": [{"id": calendar_id} for calendar_id in ids],
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

    solhealth_ids = [
        calendar_id
        for calendar_id in calendar_ids
        if calendar_id.endswith("@solhealth.co")
    ]
    others = [
        calendar_id
        for calendar_id in calendar_ids
        if not calendar_id.endswith("@solhealth.co")
    ]
    data = {}
    try:
        if solhealth_ids:
            data.update(_fetch_busy_events(solhealth_ids, use_solhealth=True))
        if others:
            data.update(_fetch_busy_events(others))
        return data
    except HttpError as error:
        logger.error(
            "Freebusy query error",
            extra={"calendar_ids": calendar_ids, "error": str(error)},
        )
        if raise_error:
            raise error
        return None


def create_gcalendar_event(
    summary: str,
    start_time: datetime,
    attendees: list[dict],
    duration_minutes: int = 45,
    description: str | None = None,
    join_url: str | None = None,
    timezone: str = "UTC",
) -> dict | None:
    """
    Create an event directly in attendee's calendar

    Args:
        summary: Event title
        start_time: Event start time
        attendees: List of attendee dictionaries with 'email' and 'name' keys
        duration_minutes: Event duration in minutes
        description: Event description (supports HTML)
        join_url: Event call url (can be physical or virtual meeting link)
        timezone: Timezone for the event (default: UTC)

    Returns:
        dict: Created event data or None if failed
    """
    service = _get_service(settings.CONTACT_EMAIL)
    try:
        end_time = start_time + timedelta(minutes=duration_minutes)

        # Convert times to ISO format with timezone
        start_time_iso = start_time.astimezone(UTC).isoformat()
        end_time_iso = end_time.astimezone(UTC).isoformat()

        event: dict = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time_iso,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time_iso,
                "timeZone": timezone,
            },
            "attendees": [
                {
                    "email": attendee["email"],
                    "displayName": attendee["name"],
                    "responseStatus": "accepted",
                }
                for attendee in attendees
            ],
            "reminders": {"useDefault": True},
        }

        if join_url:
            event["conferenceData"] = {
                "entryPoints": [
                    {
                        "entryPointType": "video",
                        "uri": join_url,
                        "label": "meet.google.com"
                        if join_url.__contains__("meet.google.com")
                        else "SolHealth Video Call",
                    }
                ],
                "conferenceSolution": {
                    "key": {
                        "type": "hangoutsMeet"
                        if join_url.__contains__("meet.google.com")
                        else "addOn"
                    },
                    "name": "Google Meet"
                    if join_url.__contains__("meet.google.com")
                    else "SolHealth Video Call",
                },
            }

        # Create event in calendar
        created_event = (
            service.events()
            .insert(
                calendarId="primary",
                body=event,
                sendUpdates="all",
                supportsAttachments=True,
                conferenceDataVersion=1 if join_url else 0,
            )
            .execute()
        )

        logger.info(
            "Google Calendar event created successfully",
            extra={
                "event_id": created_event.get("id"),
                "summary": summary,
                "attendees": attendees,
            },
        )
        return created_event

    except HttpError as e:
        logger.error(
            "Failed to create Google Calendar event",
            extra={"error": str(e), "summary": summary, "attendees": attendees},
        )
        return None
    finally:
        service.close()


def update_gcalendar_event(
    event_id: str,
    start_time: datetime | None = None,
    duration_minutes: int = 45,
    timezone: str = "UTC",
) -> dict | None:
    """
    Update an existing Google Calendar event

    Args:
        event_id: ID of the event to update
        start_time: New event start time (optional)
        duration_minutes: Event duration in minutes
        timezone: Timezone for the event (default: UTC)

    Returns:
        dict: Updated event data or None if failed
    """
    service = _get_service(settings.CONTACT_EMAIL)
    try:
        # First get the existing event
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        # Update fields if provided
        if start_time:
            event["start"] = {
                "dateTime": start_time.astimezone(UTC).isoformat(),
                "timeZone": timezone,
            }
            event["end"] = {
                "dateTime": (start_time + timedelta(minutes=duration_minutes))
                .astimezone(UTC)
                .isoformat(),
                "timeZone": timezone,
            }

        # Update the event
        updated_event = (
            service.events()
            .update(
                calendarId="primary",
                eventId=event_id,
                body=event,
                sendUpdates="all",
                supportsAttachments=True,
                conferenceDataVersion=1 if event.get("conferenceData") else 0,
            )
            .execute()
        )

        return updated_event

    except HttpError as e:
        logger.error(
            "Update calendar event error",
            extra={"event_id": event_id, "error": str(e)},
        )
        return None
    finally:
        service.close()


def delete_gcalendar_event(
    event_id: str,
    send_updates: str = "all",
):
    """
    Delete an event from Google Calendar

    Args:
        event_id: ID of the event to delete
        send_updates: Whether to send notifications about the deletion
            - "all": Send notifications to all attendees
            - "externalOnly": Send notifications only to non-Google Calendar users
            - "none": Don't send any notifications

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    service = _get_service(settings.CONTACT_EMAIL)
    try:
        service.events().delete(
            calendarId="primary",
            eventId=event_id,
            sendUpdates=send_updates,
        ).execute()

        logger.info(
            "Google Calendar event deleted successfully",
            extra={"event_id": event_id},
        )

    except HttpError as e:
        logger.error(
            "Failed to delete Google Calendar event",
            extra={"event_id": event_id, "error": str(e)},
        )
    finally:
        service.close()


def get_event_from_gcalendar(
    summary: str, calendar_id: str, date_start: str, date_end: str
) -> dict | None:
    events = get_events_from_gcalendar(
        calendar_id=calendar_id, time_min=date_start, time_max=date_end
    )
    for event in events:
        if event["summary"] == summary:
            return event
    return None
