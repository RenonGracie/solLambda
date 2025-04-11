from datetime import datetime, timedelta
from time import sleep

from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint
from googleapiclient.errors import HttpError
from pyairtable import Api

from src.models.api.base import AdminPass, Email
from src.models.api.calendar import (
    CalendarEvents,
    EventQuery,
    TherapistEmails,
    TherapistEvents,
)
from src.models.api.client_match import MatchedTherapists, MatchQuery
from src.models.api.error import Error
from src.models.api.therapist_s3 import MediaQuery, MediaLink
from src.models.api.therapists import Therapists, Therapist, AvailableSlots
from src.utils.constants.contants import DEFAULT_ZONE
from src.utils.google.calendar_event_parser import parse_calendar_events
from src.utils.google.google_calendar import (
    get_events_from_gcalendar,
    insert_email_to_gcalendar,
    gcalendar_list,
)
from src.utils.matching_algorithm.match import match_client_with_therapists
from src.utils.settings import settings
from src.utils.s3 import get_media_url
from src.utils.therapists.airtable import save_therapists
from src.utils.therapists.appointments_utils import (
    process_appointments,
    events_from_calendar_to_appointments,
)
from src.utils.therapists.therapist_data_utils import provide_therapist_slots

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
        table, query.response_id, query.limit, query.last_index
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
        return jsonify(
            Error(error=e.reason, details=e.error_details).dict()
        ), e.status_code


@therapist_api.get("/media", responses={200: MediaLink}, summary="Get the media link")
def get_video_link(query: MediaQuery):
    url = get_media_url(user_id=query.email, s3_media_type=query.type)
    return jsonify({"url": url}), 200


@therapist_api.get(
    "with_calendar",
    responses={200: TherapistEmails},
    summary="Get therapists who shared their calendar",
)
def with_calendar():
    emails = list(
        map(
            lambda therapist: therapist["fields"].get("Calendar")
            or therapist["fields"].get("Email")
            or therapist["fields"].get("Notes"),
            table.all(),
        )
    )
    shared = []
    errors = []
    items = gcalendar_list()
    items = {item["id"] for item in items}
    for email in emails:
        if items.__contains__(email) is False:
            try:
                insert_email_to_gcalendar(email)
                shared.append(email)
                print("Email added", email)
                sleep(0.5)
            except HttpError as e:
                print("Email error", email, e)
                errors.append({"email": email, "error": str(e)})
                sleep(0.5)
                pass
    return jsonify({"emails": list(items) + shared, "errors": errors}), 200


@therapist_api.post(
    "set_events",
    responses={204: None},
    summary="Save therapist's calendar events",
    doc_ui=False,
)
def set_events(query: AdminPass, body: TherapistEvents):
    if not query.admin_password.__eq__(settings.ADMIN_PASSWORD):
        return jsonify({}), 401
    else:
        process_appointments(body)
        return jsonify({}), 204


@therapist_api.get(
    "slots",
    responses={200: AvailableSlots},
    summary="Get therapist's available slots by calendar email",
)
def free_slots(query: Email):
    appointments = events_from_calendar_to_appointments(query.email)
    first_week_slots = []
    second_week_slots = []
    now = datetime.now(tz=DEFAULT_ZONE).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    for day in range(7):
        for hour in range(15):
            first_week_slots.append(now + timedelta(hours=hour, days=day))
            second_week_slots.append(now + timedelta(hours=hour, days=day + 7))
    slots = provide_therapist_slots(
        now, first_week_slots, second_week_slots, appointments, []
    )
    return jsonify({"available_slots": slots}), 200
