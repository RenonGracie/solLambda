from src.db.database import with_database
from src.models.db.clients import (
    ClientSignup,
    create_from_typeform_data,
    update_from_typeform_data,
)
from src.utils.intakeq_bot.bot import create_new_form
from src.utils.request_utils import intakeq
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
    create_on_intakeq = False
    if not form:
        db.add(create_from_typeform_data(response_id, data))
        create_on_intakeq = True
    else:
        update_from_typeform_data(response_id, form, data)
        if not form.first_name.__eq__(data.first_name) or not form.last_name.__eq__(
            data.last_name
        ):
            create_on_intakeq = True
    if create_on_intakeq:
        user_data = create_new_form(data)
        intakeq({"user": user_data, "sheetURL": f"{base_url}_bot"})
