from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.db.database import with_database
from src.models.api.events import AnalyticsEvent
from src.models.db.analytic_event import AnalyticEvent
from src.utils.request_utils import sent_analytics_event


REGISTRATION_EVENT = "registration"
CALL_SCHEDULED_EVENT = "call_scheduled"

USER_EVENT_TYPE = "user"
INTAKEQ_EVENT_TYPE = "intakeQ"


def _send_event(
    db,
    client_id: str,
    email: str,
    user_id: str,
    session_id: str,
    name: str | None,
    value: str | None,
    event_type: str | None = None,
    var_1: str | None = None,
    var_2: str | None = None,
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
    now = datetime.now()

    if params is None:
        params = {}

    event = AnalyticEvent()
    event.client_id = client_id
    event.user_id = user_id
    event.email = email
    event.session_id = session_id

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


def send_ga_event(
    client_id: str,
    email: str,
    user_id: str,
    session_id: str,
    name: str | None,
    value: str | None = None,
    event_type: str | None = None,
    var_1: str | None = None,
    var_2: str | None = None,
    params: dict | None = None,
    utm_source: str | None = None,
    utm_medium: str | None = None,
    utm_campaign: str | None = None,
    utm_adid: str | None = None,
    utm_adgroup: str | None = None,
    utm_content: str | None = None,
    utm_term: str | None = None,
    clid: str | None = None,
    database: Session | None = None,
):
    @with_database
    def send_event(db):
        _send_event(
            db,
            client_id,
            email,
            user_id,
            session_id,
            name,
            value,
            event_type,
            var_1,
            var_2,
            params,
            utm_source,
            utm_medium,
            utm_campaign,
            utm_adid,
            utm_adgroup,
            utm_content,
            utm_term,
            clid,
        )

    if database:
        _send_event(
            database,
            client_id,
            email,
            user_id,
            session_id,
            name,
            value,
            event_type,
            var_1,
            var_2,
            params,
            utm_source,
            utm_medium,
            utm_campaign,
            utm_adid,
            utm_adgroup,
            utm_content,
            utm_term,
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
