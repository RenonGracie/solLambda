from src.db.database import with_database
from src.models.db.signup_form import ClientSignup, create_from_typeform_data
from src.utils.event_utils import REGISTRATION_EVENT, USER_EVENT_TYPE, send_ga_event
from src.utils.intakeq.bot.bot import create_client_model, create_new_form
from src.utils.logger import get_logger
from src.utils.request_utils import intakeq, save_update_client
from src.utils.settings import settings
from src.utils.typeform.typeform_parser import TypeformData

logger = get_logger()


@with_database
def process_typeform_data(db, response_json: dict):
    response_id = response_json["form_response"]["token"]

    if db.query(ClientSignup).filter_by(response_id=response_id).first():
        return

    form_response = response_json["form_response"]

    hidden = form_response.get("hidden", {})

    # Extract payment type from Typeform hidden fields, defaulting to out_of_pocket
    payment_type = hidden.get("paymentType", "out_of_pocket")

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
    # Save payment type on the form
    form.payment_type = payment_type
    if form.state.__eq__("I don't see my state"):
        db.add(form)
        return

    # Create / update the IntakeQ client in the relevant account
    response = save_update_client(
        create_client_model(form).dict(), payment_type=payment_type
    )

    client_json = response.json()
    user_id = client_json.get("Id") or client_json.get("ClientId") or response_id

    # Store UTM params against the user/client
    form.setup_utm(user_id, hidden)

    logger.debug("intakeQ response", extra={"response": response.json()})

    if payment_type == "out_of_pocket":
        # Send data to IntakeQ bot only for cash-pay clients (legacy behaviour)
        user_data = create_new_form(form)
        intakeq(
            {
                "user": user_data,
                "spreadsheet_id": settings.SPREADSHEET_ID,
                "form_url": settings.INTAKEQ_SIGNUP_FORM,
                "env": "live" if settings.ENV == "prod" else settings.ENV,
                "response_id": response_id,
            },
            payment_type=payment_type,
        )

    # Persist form to DB
    db.add(form)

    # Send Google Analytics event with payment_type param
    send_ga_event(
        client=form,
        name=REGISTRATION_EVENT,
        params={"payment_type": payment_type},
        event_type=USER_EVENT_TYPE,
    )
