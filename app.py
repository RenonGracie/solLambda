import json
from datetime import datetime

import sentry_sdk
from flask import jsonify, request
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

# Fixed import - was causing ModuleNotFoundError
from src.db.database import db

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
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        process_typeform_data(data)
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error("Typeform webhook error", extra={"error": str(e)})
        return jsonify({"error": "Internal server error"}), 500


@app.post(
    "/intakeq_hook",
    tags=[Tag(name="Webhook")],
    summary="Webhook for IntakeQ Appointments",
)
def intakeq_hook():
    try:
        data = request.get_json()
        logger.info("Appointment webhook triggered", extra={"data": data})
        process_appointment(data)
        return "", 204
    except Exception as e:
        logger.error("IntakeQ appointment webhook error", extra={"error": str(e)})
        return "", 500


@app.post(
    "/intakeq_invoice_hook",
    tags=[Tag(name="Webhook")],
    summary="Webhook for IntakeQ Invoices",
)
def intakeq_invoice_hook():
    try:
        data = request.get_json()
        process_invoice(data)
        return "", 204
    except Exception as e:
        logger.error("IntakeQ invoice webhook error", extra={"error": str(e)})
        return "", 500


# Add the missing admin endpoint
@app.post(
    "/admin/add-payment-type",
    tags=[Tag(name="Admin")],
    responses={200: SuccessResponse},
    summary="Add payment type to existing signup forms",
)
def add_payment_type():
    try:
        admin_password = request.headers.get("X-Admin-Password")
        if admin_password != settings.ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401
        
        # First check if the column exists, if not add it
        try:
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'signup' 
                AND column_name = 'payment_type'
            """))
            
            if not result.fetchone():
                # Column doesn't exist, add it
                db.execute(text("""
                    ALTER TABLE signup 
                    ADD COLUMN payment_type VARCHAR(50) DEFAULT 'out_of_pocket'
                """))
                logger.info("Added payment_type column to signup table")
            
            # Update all signup forms without payment_type to have default value
            result = db.execute(text("""
                UPDATE signup 
                SET payment_type = 'out_of_pocket' 
                WHERE payment_type IS NULL
            """))
            updated_count = result.rowcount
            db.commit()
            
            return jsonify({
                "success": True, 
                "message": f"Updated {updated_count} records with payment_type"
            }), 200
            
        except Exception as db_error:
            db.rollback()
            logger.error("Database operation failed", extra={"error": str(db_error)})
            raise db_error
            
    except Exception as e:
        logger.error("Admin add payment type error", extra={"error": str(e)})
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)