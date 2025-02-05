from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint
from pyairtable import Api

from src.models.api.calendar import CalendarEvents, EventQuery
from src.models.api.client_match import MatchedTherapists, MatchQuery
from src.models.api.clients import ClientShort
from src.models.api.therapist_s3 import VideoQuery, VideoLink
from src.models.api.therapists import Therapists, Therapist
from src.utils.google_calendar import get_events_from_gcalendar
from src.utils.matching_algorithm import match_client_with_therapists
from src.utils.settings import settings
from src.utils.s3 import get_video_url

__tag = Tag(name="Therapists")
therapist_api = APIBlueprint(
    "therapists",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/therapists",
)

api = Api(settings.AIRTABLE_API_KEY)
table = api.table("appeJMQ59lRzIADPP", "tblpLJff9xwTB54yd")


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
        query.response_id, therapists, query.limit
    )
    return jsonify(
        {"client": ClientShort(**client.__dict__).dict(), "therapists": matched}
    ), 200


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


@therapist_api.get("/video", responses={200: VideoLink}, summary="Get the video link")
def get_video_link(query: VideoQuery):
    url = get_video_url(query.video_id)
    return jsonify({"url": url}), 200
