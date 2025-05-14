from src.models.db.signup_form import ClientSignup
from src.utils.logger import get_logger
from src.utils.request_utils import sent_analytics_event

REGISTRATION_EVENT = "ClientCreated"
CALL_SCHEDULED_EVENT = "CallScheduled"

USER_EVENT_TYPE = "User"
APPOINTMENT_EVENT_TYPE = "Appointment"
INVOICE_EVENT_TYPE = "Invoice"

logger = get_logger()


def send_ga_event(
    client: ClientSignup,
    name: str | None,
    event_type: str | None = None,
    params: dict | None = None,
):
    if params is None:
        params = {}

    utm = client.utm
    client_id = utm.get("client_id")

    utm_medium = utm.get("utm_medium")
    utm_source = utm.get("utm_source")
    utm_campaign = utm.get("utm_campaign")
    utm_content = utm.get("utm_content")
    utm_term = utm.get("utm_term")
    utm_adid = utm.get("utm_adid")
    utm_adgroup = utm.get("utm_adgroup")

    user_id = utm.get("user_id")

    if event_type:
        params["type"] = event_type
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

    event = {
        "client_id": client_id,
        "user_id": str(user_id),
        "events": [{"name": name, "params": params}],
    }
    logger.info("Google Analytics event", extra={"event": event})
    response = sent_analytics_event(event)
    logger.info("Google Analytics response", extra={"response": str(response)})
