from src.db.database import with_database
from src.models.db.signup_form import ClientSignup
from src.utils.event_utils import send_ga_event, INVOICE_EVENT_TYPE


@with_database
def process_invoice(db, data: dict):
    invoice = data["Invoice"]

    client = db.query(ClientSignup).filter_by(email=invoice["ClientEmail"]).first()

    event = data["EventType"]

    client_id = invoice.get("ClientIdNumber")
    if client:
        send_ga_event(
            database=db,
            client_id=client_id,
            user_id=client.utm.get("user_id"),
            email=client.email,
            session_id=client.utm.get("session_id"),
            name=event,
            value=invoice.get("TotalAmount"),
            var_1=client_id,
            var_2=invoice.get("Id"),
            params={"status": invoice["Status"]},
            event_type=INVOICE_EVENT_TYPE,
        )
