from src.db.database import with_database
from src.models.db.signup_form import ClientSignup, create_empty_client_form
from src.utils.event_utils import send_ga_event, INVOICE_EVENT_TYPE


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

    user_id = client.utm.get("user_id")

    send_ga_event(
        database=db,
        client=client,
        name=event,
        value=invoice.get("TotalAmount"),
        var_1=user_id,
        var_2=invoice.get("Id"),
        params={"status": invoice["Status"]},
        event_type=INVOICE_EVENT_TYPE,
    )
