from flask import jsonify, request
from flask_openapi3 import Tag, Info, OpenAPI

from src.models.api.base import SuccessResponse
from src.models.db.clients import (
    ClientSignup,
    create_from_typeform_data,
    update_from_typeform_data,
)
from src.routes import client_api, appointment_api, therapist_api
from src.utils.intakeq_bot.bot import create_new_form
from src.utils.request_utils import intakeq
from src.utils.typeform_utils import TypeformData
from src.db.database import db

__jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
__security_schemes = {"jwt": __jwt}

info = Info(title="SolHealth API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=__security_schemes)

app.register_api(client_api)
app.register_api(appointment_api)
app.register_api(therapist_api)


@app.post(
    "/hook",
    tags=[Tag(name="Webhook")],
    responses={200: SuccessResponse},
    summary="Webhook for typeform",
)
def typeform_webhook():
    print(request)
    response_json = request.get_json()
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
    form = (
        db.query(ClientSignup)
        .filter_by(
            first_name=data.first_name, last_name=data.last_name, email=data.email
        )
        .first()
    )
    if not form:
        db.add(create_from_typeform_data(response_id, data))
        db.commit()
        user_data = create_new_form(data)
        intakeq({"user": user_data, "sheetURL": f"{request.base_url}_bot"})
    else:
        update_from_typeform_data(response_id, form, data)
        db.commit()
    return jsonify({"success": True}), 200


@app.post("/hook_bot", tags=[Tag(name="Webhook")], summary="Webhook for bot")
def bot_hook():
    return "", 200


@app.post("/intakeq_hook", tags=[Tag(name="Webhook")], summary="Webhook for IntakeQ Appointments")
def intakeq_hook():
    return "", 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
