from flask import jsonify, request
from flask_openapi3 import Tag, Info, OpenAPI

from src.models.api.base import SuccessResponse
from src.routes import client_api, appointment_api, therapist_api
from src.routes.client_signup_forms import client_signup_api
from src.utils.therapists.intakeq_webhook_appointment_utils import process_appointment
from src.utils.typeform.typeform_utils import process_typeform_data

__jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
__security_schemes = {"jwt": __jwt}

info = Info(title="SolHealth API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=__security_schemes)

app.register_api(client_api)
app.register_api(client_signup_api)
app.register_api(appointment_api)
app.register_api(therapist_api)


@app.after_request
def set_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin and origin.endswith("solhealth.co"):
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Origin"] = origin
    return response


@app.post(
    "/hook",
    tags=[Tag(name="Webhook")],
    responses={200: SuccessResponse},
    summary="Webhook for typeform",
)
def typeform_webhook():
    print(request)
    process_typeform_data(request.get_json(), request.base_url)
    return jsonify({"success": True}), 200


@app.post("/hook_bot", tags=[Tag(name="Webhook")], summary="Webhook for bot")
def bot_hook():
    return "", 200


@app.post(
    "/intakeq_hook",
    tags=[Tag(name="Webhook")],
    summary="Webhook for IntakeQ Appointments",
)
def intakeq_hook():
    process_appointment(request.get_json())
    return "", 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
