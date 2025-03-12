from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint
from googleapiclient.errors import HttpError
from pyairtable import Api

from src.models.api.calendar import (
    CalendarEvents,
    EventQuery,
    TherapistEmails,
    TherapistEvents,
)
from src.models.api.client_match import MatchedTherapists, MatchQuery
from src.models.api.therapist_s3 import MediaQuery, MediaLink
from src.models.api.therapists import Therapists, Therapist
from src.utils.google_calendar import (
    get_events_from_gcalendar,
    insert_email_to_gcalendar,
    gcalendar_list,
)
from src.utils.matching_algorithm.match import match_client_with_therapists
from src.utils.settings import settings
from src.utils.s3 import get_media_url
from src.utils.therapists.appointments_utils import process_appointments

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
    return jsonify({"therapists": therapists}), 200


@therapist_api.get(
    "/match", responses={200: MatchedTherapists}, summary="Match client with therapists"
)
def match(query: MatchQuery):
    therapists = list(map(lambda therapist: Therapist(therapist), table.all()))
    client, matched = match_client_with_therapists(
        query.response_id, therapists, query.limit, query.last_index
    )
    if client is None:
        return jsonify({"client": None, "therapists": []}), 200

    return jsonify({"client": client, "therapists": matched}), 200


@therapist_api.get(
    "/calendar_events", responses={200: CalendarEvents}, summary="Get calendar events"
)
def get_events(query: EventQuery):
    events = get_events_from_gcalendar(
        calendar_id=query.calendar_id,
        time_min=query.time_min,
        time_max=query.time_max,
        max_results=query.max_results,
    )
    return jsonify({"events": events}), 200


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
            lambda therapist: therapist["fields"].get("Email")
            or therapist["fields"].get("Notes"),
            table.all(),
        )
    )
    shared = []
    errors = []
    items = gcalendar_list()  ##nhi.vo@columbia.edu
    items = {item["id"] for item in items}
    for email in emails:
        if items.__contains__(email) is False:
            try:
                insert_email_to_gcalendar(email)
                shared.append(email)
                print("Email added", email)
            except HttpError as e:
                print("Email error", email, e)
                errors.append({"email": email, "error": str(e)})
                pass
    return jsonify({"emails": list(items) + shared, "errors": errors}), 200


@therapist_api.post(
    "set_events",
    responses={204: None},
    summary="Save therapist's calendar events",
)
def set_events(body: TherapistEvents):
    process_appointments(body)
    return jsonify({}), 204
