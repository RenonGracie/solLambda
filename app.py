import json
from datetime import datetime

import sentry_sdk
from flask import jsonify, request
from flask_openapi3 import Info, OpenAPI, Tag
from sentry_sdk.integrations.flask import FlaskIntegration

from src.models.api.base import SuccessResponse
from src.routes import (
    appointment_api,
    client_api,
    client_signup_api,
    emails_api,
    intakeq_forms_api,
    therapist_api,
)
from src.utils.logger import add_request_id, get_logger
from src.utils.settings import settings
from src.utils.webhooks.intakeq_webhook_appointment_utils import process_appointment
from src.utils.webhooks.intakeq_webhook_invoices_utils import process_invoice
from src.utils.webhooks.typeform_webhook_utils import process_typeform_data

# Initialize Sentry
if settings.ENV != "dev":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,  # Replace with your DSN from Sentry
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,  # Sample 10% of transactions for performance monitoring
        environment=settings.ENV,  # Change to "production" for production environment
    )

__jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
__security_schemes = {"jwt": __jwt}


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


info = Info(title="SolHealth API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=__security_schemes)
app.json.sort_keys = False
app.json_encoder = CustomJSONEncoder

# Configure Flask to use ISO format for datetime
app.config["JSON_AS_ASCII"] = False
app.config["JSONIFY_MIMETYPE"] = "application/json"
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["JSONIFY_DATETIME_FORMAT"] = "iso"

# Setup logging
logger = get_logger()


# Add request ID middleware
@app.before_request
def before_request():
    add_request_id()


app.register_api(client_api)
app.register_api(client_signup_api)
app.register_api(appointment_api)
app.register_api(therapist_api)
app.register_api(intakeq_forms_api)
app.register_blueprint(emails_api)


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
    process_typeform_data(request.get_json())
    return jsonify({"success": True}), 200


@app.post(
    "/intakeq_hook",
    tags=[Tag(name="Webhook")],
    summary="Webhook for IntakeQ Appointments",
)
def intakeq_hook():
    data = request.get_json()
    logger.info("Appointment webhook triggered", extra={"data": data})
    process_appointment(data)
    return "", 200


@app.post(
    "/intakeq_invoice_hook",
    tags=[Tag(name="Webhook")],
    summary="Webhook for IntakeQ Invoices",
)
def intakeq_invoice_hook():
    data = request.get_json()
    process_invoice(data)
    return "", 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
