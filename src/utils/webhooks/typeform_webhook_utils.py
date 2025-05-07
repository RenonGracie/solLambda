from src.db.database import with_database
from src.models.db.signup_form import create_from_typeform_data, ClientSignup
from src.utils.event_utils import send_ga_event, REGISTRATION_EVENT, USER_EVENT_TYPE
from src.utils.intakeq.bot.bot import create_new_form, create_client_model
from src.utils.request_utils import intakeq, save_update_client
from src.utils.settings import settings
from src.utils.typeform.typeform_parser import TypeformData
from src.utils.logger import get_logger

logger = get_logger()


@with_database
def process_typeform_data(db, response_json: dict):
    response_id = response_json["form_response"]["token"]

    if db.query(ClientSignup).filter_by(response_id=response_id).first():
        return

    form_response = response_json["form_response"]
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
    if form.state.__eq__("I don't see my state"):
        db.add(form)
        return

    response = save_update_client(create_client_model(data).dict())

    client_json = response.json()
    user_id = client_json.get("Id") or client_json.get("ClientId")
    client_id, session_id = form.setup_utm(user_id)

    logger.debug("intakeQ response", extra={"response": response.json()})
    send_ga_event(
        database=db,
        client_id=client_id,
        user_id=user_id,
        email=form.email,
        session_id=session_id,
        name=REGISTRATION_EVENT,
        event_type=USER_EVENT_TYPE,
    )

    db.add(form)
    user_data = create_new_form(form)
    intakeq(
        {
            "user": user_data,
            "spreadsheet_id": settings.SPREADSHEET_ID,
            "form_url": settings.INTAKEQ_SIGNUP_FORM,
            "env": "live" if settings.ENV == "prod" else settings.ENV,
            "response_id": response_id,
        }
    )
