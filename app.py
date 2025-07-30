import json
from datetime import datetime

import sentry_sdk
from flask import jsonify, request, make_response
from flask_openapi3 import Info, OpenAPI, Tag
from sentry_sdk.integrations.flask import FlaskIntegration

from src.models.api.base import SuccessResponse
from src.routes import (
    appointment_api,
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


# -------------------------------------------------
# CORS helpers
# -------------------------------------------------
# NOTE: Placed close to the top so it can be reused in any route definitions below.


def is_origin_allowed(origin):
    """Check if the origin is allowed based on configuration."""
    if not origin:
        return False

    # Explicitly allowed origins from the environment
    if origin in settings.ALLOWED_CORS_ORIGINS:
        return True

    # Fallback: allow any sub-domain of solhealth.co
    if origin.endswith("solhealth.co"):
        return True

    return False


# ---------------------------------------------------------------------------
# CORS pre-flight handler – must come before other before_request middleware
# ---------------------------------------------------------------------------


@app.before_request
def handle_cors_preflight():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")

        allowed_origins = {
            "https://stg.solhealth.co",
            "https://solhealth.co",
            "https://www.solhealth.co",
            "https://api.stg.solhealth.co",
            "https://solpaymentflow-production.up.railway.app",
        }

        if origin and (origin in allowed_origins or origin.endswith("solhealth.co")):
            response = jsonify({"status": "OK"})
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response

# ---------------------------------------------------------------------------
# Add request ID middleware (renamed)
# ---------------------------------------------------------------------------


@app.before_request
def add_request_id_middleware():
    # Skip adding request ID for OPTIONS requests
    if request.method != "OPTIONS":
        add_request_id()


app.register_api(client_signup_api)
app.register_api(appointment_api)
app.register_api(therapist_api)
app.register_api(intakeq_forms_api)
app.register_blueprint(emails_api)


# ---------------------------------------------------------------------------
# After-request CORS headers
# ---------------------------------------------------------------------------


@app.after_request
def set_cors_headers(response):
    origin = request.headers.get("Origin")

    allowed_origins = {
        "https://stg.solhealth.co",
        "https://solhealth.co",
        "https://www.solhealth.co",
        "https://api.stg.solhealth.co",
        "https://solpaymentflow-production.up.railway.app",
    }

    # Allow if origin is explicitly allowed or ends with solhealth.co
    if origin and (origin in allowed_origins or origin.endswith("solhealth.co")):
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-Requested-With"
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"

    return response

# ---------------------------------------------------------------------------
# Deprecated: old pre-flight handler (kept to avoid reference errors, no-op)
# ---------------------------------------------------------------------------


def _deprecated_handle_preflight():
    """This function has been superseded by handle_cors_preflight."""
    pass


@app.post(
    "/hook",
    tags=[Tag(name="Webhook")],
    responses={200: SuccessResponse},
    summary="Webhook for typeform",
)
def typeform_webhook():
    process_typeform_data(request.get_json())
    return jsonify({"success": True}), 200

@app.get("/run-migration-temp", summary="Temporary migration endpoint")
def run_migration_temp():
    from migrate import run_migration
    try:
        run_migration()
        return jsonify({"success": True, "message": "Migration completed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.post(
    "/intakeq_hook",
    tags=[Tag(name="Webhook")],
    summary="Webhook for IntakeQ Appointments",
)
def intakeq_hook():
    data = request.get_json()
    logger.info("Appointment webhook triggered", extra={"data": data})
    process_appointment(data)
    return "", 204


@app.post(
    "/intakeq_invoice_hook",
    tags=[Tag(name="Webhook")],
    summary="Webhook for IntakeQ Invoices",
)
def intakeq_invoice_hook():
    data = request.get_json()
    process_invoice(data)
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
