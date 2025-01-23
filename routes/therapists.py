from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint
from pyairtable import Api

from models.calendar import CalendarEvents, EventQuery
from models.client_match import MatchedTherapists, ClientMatchData, MatchQuery
from models.therapists import TherapistsTable
from utils.google_calendar import get_events_from_gcalendar
from utils.matching_algorithm import match_client_with_therapists
from utils.settings import settings

__tag = Tag(name="Therapists")
therapist_api = APIBlueprint("therapists", __name__, abp_tags=[__tag], abp_security=[{"jwt": []}], url_prefix="/therapists")

api = Api(settings.AIRTABLE_API_KEY)
table = api.table('appeJMQ59lRzIADPP', 'tblpLJff9xwTB54yd')

@therapist_api.get("", responses={200: TherapistsTable}, summary="Get therapists table")
def get_therapists():
    return jsonify({"table" : table.all()}), 200


@therapist_api.post("/match", responses={200: MatchedTherapists}, summary="Match client with therapists")
def match(body: ClientMatchData, query: MatchQuery):
    matched = match_client_with_therapists(body.model_dump(), table.all(), query.limit)
    return jsonify({"matched" : matched}), 200


@therapist_api.get("/calendar_events", responses={200: CalendarEvents}, summary="Get calendar events")
def get_events(query: EventQuery):
    events = get_events_from_gcalendar(calendar_id=query.calendar_id, time_min=query.time_min, time_max=query.time_max, max_results=query.max_results)
    return jsonify({"events" : events}), 200