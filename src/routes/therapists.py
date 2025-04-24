from datetime import datetime, timedelta

from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint
from googleapiclient.errors import HttpError
from pyairtable import Api

from src.models.api.base import Email
from src.models.api.calendar import (
    CalendarEvents,
    EventQuery,
)
from src.models.api.client_match import MatchedTherapists, MatchQuery
from src.models.api.error import Error
from src.models.api.therapist_s3 import MediaQuery, MediaLink
from src.models.api.therapists import Therapists, Therapist, AvailableSlots
from src.utils.constants.contants import DEFAULT_ZONE, DATE_FORMAT
from src.utils.google.calendar_event_parser import parse_calendar_events
from src.utils.google.google_calendar import (
    get_events_from_gcalendar,
    get_busy_events_from_gcalendar,
)
from src.utils.logger import get_logger
from src.utils.matching_algorithm.match import (
    match_client_with_therapists,
    provide_therapist_slots,
)
from src.utils.s3 import get_media_url
from src.utils.settings import settings
from src.utils.therapists.airtable import save_therapists

__tag = Tag(name="Therapists")
therapist_api = APIBlueprint(
    "therapists",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/therapists",
)

api = Api(settings.AIRTABLE_API_KEY)
table = api.table(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_ID)

logger = get_logger()


@therapist_api.get("", responses={200: Therapists}, summary="Get therapists table")
def get_therapists():
    therapists = list(map(lambda therapist: Therapist(therapist).dict(), table.all()))
    save_therapists(therapists)
    return jsonify({"therapists": therapists}), 200


@therapist_api.get(
    "/match", responses={200: MatchedTherapists}, summary="Match client with therapists"
)
def match(query: MatchQuery):
    client, matched = match_client_with_therapists(
        query.response_id, query.limit, query.last_index
    )
    if client is None:
        return jsonify({"client": None, "therapists": []}), 200

    return jsonify({"client": client, "therapists": matched}), 200


@therapist_api.get(
    "/calendar_events",
    responses={200: CalendarEvents, 500: Error},
    summary="Get calendar events",
)
def get_events(query: EventQuery):
    now = datetime.now()
    try:
        events = get_events_from_gcalendar(
            calendar_id=query.calendar_id,
            time_min=f"{query.date_min or now.strftime('%Y-%m-%d')}T00:00:00+0000",
            time_max=f"{query.date_max or (now + timedelta(days=14)).strftime('%Y-%m-%d')}T00:00:00+0000",
            max_results=query.max_results,
            raise_error=True,
        )
        return jsonify({"data": parse_calendar_events(events)}), 200
    except HttpError as e:
        details = []
        if isinstance(e.error_details, list):
            details = e.error_details
        else:
            details.append(e.error_details)
        return jsonify(Error(error=e.reason, details=details).dict()), e.status_code


@therapist_api.get("/media", responses={200: MediaLink}, summary="Get the media link")
def get_video_link(query: MediaQuery):
    url = get_media_url(user_id=query.email, s3_media_type=query.type)
    return jsonify({"url": url}), 200


@therapist_api.get(
    "slots",
    responses={200: AvailableSlots},
    summary="Get therapist's available slots by calendar email",
)
def free_slots(query: Email):
    now = datetime.now(tz=DEFAULT_ZONE).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    now_2_weeks = now + timedelta(weeks=2)
    now_str = now.strftime(DATE_FORMAT)
    now_2_weeks_str = now_2_weeks.strftime(DATE_FORMAT)
    busy = get_busy_events_from_gcalendar([query.email], now_str, now_2_weeks_str)
    first_week_slots = []
    second_week_slots = []
    now = datetime.now(tz=DEFAULT_ZONE).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    for day in range(7):
        for hour in range(15):
            first_week_slots.append(now + timedelta(hours=hour, days=day))
            second_week_slots.append(now + timedelta(hours=hour, days=day + 7))
    slots = busy.get(query.email)
    busy_slots = slots.get("busy")
    if busy_slots:
        slots = provide_therapist_slots(
            first_week_slots + second_week_slots, busy_slots
        )
    else:
        slots = first_week_slots + second_week_slots
    return jsonify({"available_slots": slots}), 200
