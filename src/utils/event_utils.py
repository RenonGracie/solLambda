from src.utils.request_utils import sent_analytics_event


REGISTRATION_EVENT = "registration"
CALL_SCHEDULED_EVENT = "call_scheduled"

USER_EVENT_TYPE = "user"
INTAKEQ_EVENT_TYPE = "intakeQ"


def send_ga_event(
    client_id: str,
    user_id: str,
    session_id: str,
    name: str | None,
    value: str | None = None,
    event_type: str | None = None,
    params: dict | None = None,
    utm_source: str | None = None,
    utm_medium: str | None = None,
    utm_campaign: str | None = None,
    utm_adid: str | None = None,
    utm_adgroup: str | None = None,
    utm_content: str | None = None,
    utm_term: str | None = None,
    clid: str | None = None,
):
    if params is None:
        params = {}

    if value:
        params["value"] = value
    if event_type:
        params["type"] = event_type
    if session_id:
        params["session_id"] = session_id
    if utm_source:
        params["utm_source"] = utm_source
    if utm_medium:
        params["utm_medium"] = utm_medium
    if utm_campaign:
        params["utm_campaign"] = utm_campaign
    if utm_adid:
        params["utm_adid"] = utm_adid
    if utm_adgroup:
        params["utm_adgroup"] = utm_adgroup
    if utm_content:
        params["utm_content"] = utm_content
    if utm_term:
        params["utm_term"] = utm_term
    if clid:
        params["clid"] = utm_term

    sent_analytics_event(
        {
            "client_id": client_id,
            "user_id": user_id,
            "events": [{"name": name, "params": params}],
        }
    )
