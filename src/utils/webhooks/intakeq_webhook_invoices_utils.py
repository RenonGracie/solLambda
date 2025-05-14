from src.db.database import with_database
from src.models.db.signup_form import ClientSignup, create_empty_client_form
from src.utils.event_utils import INVOICE_EVENT_TYPE, send_ga_event


@with_database
def process_invoice(db, data: dict):
    invoice = data["Invoice"]

    client = db.query(ClientSignup).filter_by(email=invoice["ClientEmail"]).first()

    event = data["EventType"]
    if not client:
        user_id = invoice.get("ClientIdNumber")
        client = create_empty_client_form(user_id)
        client.email = invoice.get("ClientEmail")
        db.add(client)

    send_ga_event(
        client=client,
        name=event,
        params={
            "status": invoice["Status"],
            "total_amount": invoice.get("TotalAmount"),
            "invoice_id": invoice.get("Id"),
        },
        event_type=INVOICE_EVENT_TYPE,
    )
