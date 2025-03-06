from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from src.models.api.events import AnalyticsEventQuery, AnalyticsEvents
from src.utils.event_utils import load_events

__tag = Tag(name="Events")
events_api = APIBlueprint(
    "events",
    __name__,
    abp_tags=[__tag],
    url_prefix="/events",
)


@events_api.get("", responses={200: AnalyticsEvents}, summary="Get analytics event")
def send_event(query: AnalyticsEventQuery):
    events = load_events(query.dict())
    return jsonify({"events": events}), 200
