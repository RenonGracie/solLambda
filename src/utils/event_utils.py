from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.db.database import with_database
from src.models.api.events import AnalyticsEvent
from src.models.db.analytic_event import AnalyticEvent
from src.models.db.signup_form import ClientSignup
from src.utils.request_utils import sent_analytics_event
from src.utils.logger import get_logger


REGISTRATION_EVENT = "ClientCreated"
CALL_SCHEDULED_EVENT = "CallScheduled"

USER_EVENT_TYPE = "User"
APPOINTMENT_EVENT_TYPE = "Appointment"
INVOICE_EVENT_TYPE = "Invoice"

logger = get_logger()


def _send_event(
    db,
    client: ClientSignup,
    name: str | None,
    value: str | None,
    event_type: str | None = None,
    var_1: str | None = None,
    var_2: str | None = None,
    params: dict | None = None,
    clid: str | None = None,
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

    event = AnalyticEvent()
    event.client_id = client_id
    event.user_id = user_id
    event.email = client.email

    event.type = event_type

    event.name = name
    event.value = value
    event.params = params

    event.var_1 = var_1
    event.var_2 = var_2

    event.utm_source = utm_source
    event.utm_medium = utm_medium
    event.utm_campaign = utm_campaign
    event.utm_adid = utm_adid
    event.utm_adgroup = utm_adgroup
    event.utm_content = utm_content
    event.utm_term = utm_term
    event.clid = clid

    db.add(event)

    if event_type:
        params["type"] = event_type
    if value:
        params["value"] = value
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
    if var_1:
        params["var_1"] = var_1
    if var_2:
        params["var_2"] = var_2
    if clid:
        params["clid"] = clid

    event = {
        "client_id": client_id,
        "user_id": str(user_id),
        "events": [{"name": name, "params": params}],
    }
    logger.info("Google Analytics event", extra={"event": event})
    response = sent_analytics_event(event)
    logger.info("Google Analytics response", extra={"response": str(response)})


def send_ga_event(
    client: ClientSignup,
    name: str | None,
    value: str | None = None,
    event_type: str | None = None,
    var_1: str | None = None,
    var_2: str | None = None,
    params: dict | None = None,
    clid: str | None = None,
    database: Session | None = None,
):
    @with_database
    def send_event(db):
        _send_event(
            db,
            client,
            name,
            value,
            event_type,
            var_1,
            var_2,
            params,
            clid,
        )

    if database:
        _send_event(
            database,
            client,
            name,
            value,
            event_type,
            var_1,
            var_2,
            params,
            clid,
        )
    else:
        send_event()


@with_database
def load_events(db, query: dict):
    filter_conditions = []
    for key, value in query.items():
        if value and hasattr(AnalyticEvent, key):
            column = getattr(AnalyticEvent, key)
            filter_conditions.append(column == value)

    return [
        AnalyticsEvent(**event.__dict__).dict()
        for event in db.query(AnalyticEvent).filter(and_(*filter_conditions)).all()
    ]
