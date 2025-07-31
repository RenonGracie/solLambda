# src/utils/webhooks/typeform_webhook_utils.py
from src.db.database import with_database
from src.models.db.signup_form import ClientSignup, create_from_typeform_data
from src.utils.event_utils import REGISTRATION_EVENT, USER_EVENT_TYPE, send_ga_event
from src.utils.intakeq.bot.bot import create_client_model, create_new_form
from src.utils.logger import get_logger
from src.utils.request_utils import (
    intakeq,
    save_update_client,
    get_client_by_id,
    update_client,
)
from src.utils.settings import settings
from src.utils.typeform.typeform_parser import TypeformData

logger = get_logger()


@with_database
def process_typeform_data(db, response_json: dict):
    """
    Processes incoming webhook data from Typeform, creates or updates a client,
    and triggers downstream actions like IntakeQ and analytics events.
    This version handles both insurance and out-of-pocket payment types,
    including logic for pre-existing insurance clients.
    """
    response_id = response_json["form_response"]["token"]

    if db.query(ClientSignup).filter_by(response_id=response_id).first():
        logger.warning(f"Duplicate Typeform submission received: {response_id}")
        return

    form_response = response_json["form_response"]
    hidden = form_response.get("hidden", {})

    # Extract payment_type from hidden field (if present)
    payment_type = hidden.get("client_type")  # May be None, 'insurance', 'cash_pay', or legacy 'out_of_pocket'

    # Extract client ID for insurance clients (created during eligibility check)
    existing_client_id = hidden.get("clientId", None)

    questions_json = form_response["definition"]["fields"]
    questions = dict(map(lambda item: (item["ref"], item), questions_json))
    answers = form_response["answers"]
    json: dict = {}
    for answer in answers:
        question = questions[answer["field"]["ref"]]
        json[question["id"]] = {
            "ref": answer["field"]["ref"],
            "answer": answer[answer["type"]]
            if answer["type"] != "multiple_choice"
            else answer["choices"],
            "title": question["title"],
            "type": question["type"],
        }
    data = TypeformData(json, form_response.get("variables"))

    form = create_from_typeform_data(response_id, data)
    
    # Determine final payment_type gracefully handling legacy fields and discounts
    client_type = hidden.get("client_type") or data.get_var("client_type")
    if client_type:
        payment_type = client_type
        logger.info(
            f"Overriding payment_type with client_type: {client_type} for client {response_id}"
        )

    # Normalize legacy value 'out_of_pocket' to the new 'cash_pay'
    if payment_type == "out_of_pocket":
        logger.info(
            f"Normalizing legacy payment_type 'out_of_pocket' to 'cash_pay' for client {response_id}"
        )
        payment_type = "cash_pay"

    # Fallback logic if payment_type is still undefined
    if not payment_type:
        if form.discount == 100:
            payment_type = "free"
        elif form.discount == 50:
            payment_type = "promo_code"
        else:
            payment_type = "cash_pay"
        logger.info(
            f"Fallback payment_type resolved to: {payment_type} for client {response_id}"
        )

    # Save payment type on the form - with fallback for staging environments
    try:
        form.payment_type = payment_type
        logger.info(f"Set payment type: {payment_type} for client {response_id}")
    except AttributeError:
        logger.warning(
            f"payment_type attribute not available in this environment for client {response_id}"
        )
    
    if form.state.__eq__("I don't see my state"):
        db.add(form)
        db.commit() # Commit and exit early if state is not supported
        return

    # ------------------------------------------------------------------
    # Create or update the IntakeQ client record
    # ------------------------------------------------------------------

    if payment_type == "insurance" and existing_client_id:
        # Attempt to fetch the existing client first – if not found we'll fall back to creation
        client_response = get_client_by_id(existing_client_id, payment_type="insurance")

        if client_response and client_response.status_code == 200:
            # Prepare the updated client payload (ensure the ClientId is set)
            updated_client = create_client_model(form).dict()
            updated_client["ClientId"] = existing_client_id

            # Push the changes to IntakeQ
            update_client(updated_client, payment_type="insurance")

            client_json = client_response.json()
            user_id = existing_client_id
        else:
            # Could not fetch the client – create a new one as a fallback
            response = save_update_client(
                create_client_model(form).dict(), payment_type=payment_type
            )
            client_json = response.json()
            user_id = client_json.get("Id") or client_json.get("ClientId") or response_id
    else:
        # Cash-pay and other flows – create a new client record
        response = save_update_client(
            create_client_model(form).dict(), payment_type=payment_type
        )
        client_json = response.json()
        user_id = client_json.get("Id") or client_json.get("ClientId") or response_id

    # Store UTM params against the user/client
    form.setup_utm(user_id, hidden)

    logger.debug(
        "intakeQ response",
        extra={
            "response": client_json if payment_type != "insurance" else {"existing_client": existing_client_id}
        },
    )

    # Send data to IntakeQ bot for BOTH payment types
    user_data = create_new_form(form)

    # Add payment type so the bot can handle both insurance and cash pay flows
    user_data["payment_type"] = payment_type

    intakeq(
        {
            "user": user_data,
            "spreadsheet_id": settings.SPREADSHEET_ID,
            "form_url": settings.INTAKEQ_SIGNUP_FORM,
            "env": "live" if settings.ENV == "prod" else settings.ENV,
            "response_id": response_id,
            "payment_type": payment_type,  # Include in bot payload
        },
        payment_type=payment_type,
    )

    # Persist form to DB
    db.add(form)
    db.commit() # Commit the new client to the database

    # Send Google Analytics event with payment_type param
    send_ga_event(
        client=form,
        name=REGISTRATION_EVENT,
        params={"payment_type": payment_type},
        event_type=USER_EVENT_TYPE,
    )
    logger.info(f"Successfully processed Typeform submission for client {user_id}")