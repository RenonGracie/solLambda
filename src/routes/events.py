from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from src.models.api.events import AnalyticsEvent
from src.utils.request_utils import sent_analytics_event

__tag = Tag(name="Events")
events_api = APIBlueprint(
    "events",
    __name__,
    abp_tags=[__tag],
    url_prefix="/events",
)


@events_api.post("", responses={204: None}, summary="Test google analytics event")
def send_event(body: AnalyticsEvent):
    result = sent_analytics_event(body.dict())
    if result.status_code == 204:
        return jsonify({}), result.status_code
    return jsonify(result.json()), result.status_code
