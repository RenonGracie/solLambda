import random
import uuid

from src.db.database import with_database
from src.models.db.clients import (
    ClientSignup,
    create_from_typeform_data,
    update_from_typeform_data,
)
from src.utils.event_utils import send_ga_event, REGISTRATION_EVENT, USER_EVENT_TYPE
from src.utils.intakeq_bot.bot import create_new_form, create_client_model
from src.utils.request_utils import intakeq, save_update_client
from src.utils.typeform.typeform_parser import TypeformData


@with_database
def process_typeform_data(db, response_json: dict, base_url: str):
    questions_json = response_json["form_response"]["definition"]["fields"]
    questions = dict(map(lambda item: (item["ref"], item), questions_json))
    answers = response_json["form_response"]["answers"]
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
    data = TypeformData(json)

    response_id = response_json["form_response"]["token"]
    form = db.query(ClientSignup).filter_by(email=data.email).first()
    print("Is user new", form is None)
    if not form:
        form = create_from_typeform_data(response_id, data)
        db.add(form)
        db.flush()
    else:
        form = update_from_typeform_data(response_id, form, data)

    response = save_update_client(create_client_model(data))

    client_id = f"{random.randint(1000, 9999)}.{random.randint(1000, 9999)}"
    client_json = response.json()
    user_id = client_json.get("Id") or client_json.get("ClientId")
    session_id = str(uuid.uuid4())
    form.utm = {
        "client_id": client_id,
        "user_id": user_id,
        "session_id": session_id,
    }
    print(response.json())
    send_ga_event(
        database=db,
        client_id=client_id,
        user_id=user_id,
        email=form.email,
        session_id=session_id,
        name=REGISTRATION_EVENT,
        event_type=USER_EVENT_TYPE,
    )
    user_data = create_new_form(data)
    intakeq({"user": user_data, "sheetURL": f"{base_url}_bot"})
