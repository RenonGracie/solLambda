from flask import Blueprint, render_template_string, request
from sqlalchemy.exc import IntegrityError

from src.db.database import db
from src.models.db.unsubscribed_emails import UnsubscribedEmail
from src.utils.logger import get_logger

logger = get_logger()
emails_api = Blueprint("emails", __name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Unsubscribe Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .success {
            color: #28a745;
        }
        .error {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ status_title }}</h1>
        <p>{{ status_message }}</p>
    </div>
</body>
</html>
"""


@emails_api.get("/unsubscribe")
def unsubscribe():
    email = request.args.get("email")
    if not email:
        return render_template_string(
            HTML_TEMPLATE,
            status_title="Error",
            status_message="Email parameter is required",
        ), 400

    try:
        unsubscribed = UnsubscribedEmail(email=email)
        db.add(unsubscribed)
        db.commit()

        logger.info("Email unsubscribed successfully", extra={"email": email})

        return render_template_string(
            HTML_TEMPLATE,
            status_title="Successfully Unsubscribed",
            status_message="You have been successfully unsubscribed from our emails.",
        )
    except IntegrityError:
        db.rollback()
        return render_template_string(
            HTML_TEMPLATE,
            status_title="Already Unsubscribed",
            status_message="This email was already unsubscribed from our emails.",
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to unsubscribe email", extra={"error": str(e), "email": email}
        )
        return render_template_string(
            HTML_TEMPLATE,
            status_title="Error",
            status_message="An error occurred while processing your request. Please try again later.",
        ), 500
