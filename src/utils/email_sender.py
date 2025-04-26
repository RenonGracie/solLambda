import re
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from botocore.exceptions import ClientError

from src.db.database import db
from src.models.db.unsubscribed_emails import UnsubscribedEmail
from src.utils.calendar_utils import create_calendar_event
from src.utils.constants.contants import DEFAULT_ZONE
from src.utils.logger import get_logger
from src.utils.settings import settings

logger = get_logger()


def _is_unsubscribed(email: str) -> bool:
    return db.query(UnsubscribedEmail).filter_by(email=email).first() is not None


def extract_invitation_code(invitation_text: str | None) -> str | None:
    """
    Extract invitation code from invitation text

    Args:
        invitation_text: Full invitation text containing the code

    Returns:
        str: Extracted invitation code or None if not found
    """
    # Pattern to match "Invitation Code: " followed by any characters until the end of line
    if not invitation_text:
        return None

    pattern = r"Invitation Code:\s*(\S+)"
    match = re.search(pattern, invitation_text)

    if match:
        return match.group(1)
    return None


class EmailSender:
    def __init__(
        self, from_email: str = settings.SES_FROM_EMAIL, from_name: str = "SolHealth"
    ):
        """
        Initialize email sender with SES client

        Args:
            from_email: The email address to send from (must be verified in SES)
            from_name: The name that will appear as the sender
        """
        self.ses_client = boto3.client("ses", region_name="us-east-2")
        self.from_email = from_email
        self.from_name = from_name

    def send_email(
        self,
        base_url: str,
        therapist_name: str,
        therapist_email: str,
        client_name: str,
        client_email: str,
        start_time: datetime,
        telehealth_info: dict | None,
        duration: int = 45,
    ) -> bool:
        if _is_unsubscribed(client_email):
            logger.info(
                "Skipping email send - recipient unsubscribed",
                extra={"to": client_email},
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Sol Health Appointment"
            msg["From"] = f'"{self.from_name}" <{self.from_email}>'
            msg["To"] = client_email
            msg["List-Unsubscribe"] = f"<{base_url}/unsubscribe?email={client_email}>"

            start_time = start_time.astimezone(DEFAULT_ZONE)

            invitation_code = extract_invitation_code(telehealth_info["Invitation"])
            join_url = telehealth_info["JoinUrl"]

            # Create HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2>Your Session is Confirmed</h2>
                <p>Your appointment details have been added to the attached calendar invitation.</p>
                
                <h3>Session Details:</h3>
                <ul>
                    <li>Provider: {therapist_name}</li>
                    <li>Date: {start_time.strftime("%B %d, %Y")}</li>
                    <li>Time: {start_time.strftime("%I:%M %p")} ({
                start_time.strftime("%Z")
            })</li>
                    <li>Duration: {duration} minutes</li>
                </ul>
                
                {
                f"<h3>Join Your Session:</h3><p>Use the link below to join your scheduled video session: <br>🔗<a href='{join_url}'>join your session</a>"
                + f"<br>Invitation code: {invitation_code}</p>"
                if telehealth_info
                else ""
            }
                
                <h3>Important Information:</h3>
                <p><strong>Manage Your Appointment or Contact Your Provider</strong><br>
                Access your Client Portal to manage sessions or send messages<br>
                🔗<a href="https://solhealth.intakeq.com/portal">Client Portal</a> to manage sessions or send messages.<br>
                You can also reach your provider directly at <a href="mailto:{
                therapist_email
            }">{therapist_email}</a></p>

                <p><strong>Cancellation Policy:</strong><br>
                Please reschedule or cancel your session at least 24 hours in advance to avoid a no-show fee equal to your session cost.</p>

                <p><strong>Need Help?</strong><br>
                Email us at 📩<a href="mailto:contact@solhealth.co">contact@solhealth.co</a></p>

                <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    To unsubscribe from these emails, <a href="{
                base_url
            }/unsubscribe?email={client_email}">click here</a>
                </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, "html"))

            # Create calendar event without unsubscribe link in description
            calendar_description = "<b>Join your session</b>" \
                f"{'<br><br><b>Use the link below to join your scheduled video session:</b>' + f'<br>🔗<a href=\'{join_url}\'>Join Session</a>' + f'<br><br><b>Invitation code:</b> {invitation_code}' if telehealth_info else ''}" \
                "<br><br><b>Manage Your Appointment or Contact Your Provider</b>" \
                "<br>Access your Client Portal to manage sessions or send messages" \
                "<br>🔗<a href='https://solhealth.intakeq.com/portal'>Client Portal</a>" \
                f"<br>YYou can also reach your provider directly at <a href='mailto:{therapist_email}'>{therapist_email}</a>" \
                "<br><br><b>Cancellation Policy</b>" \
                "<br>Please reschedule or cancel your session at least 24 hours in advance to avoid a no-show fee equal to your session cost." \
                "<br><br><b>Needs Help?</b>" \
                "<br>Email us at 📩<a href='mailto:contact@solhealth.co'>contact@solhealth.co</a>"

            # Create ICS calendar event
            ics_content = create_calendar_event(
                summary=f"Sol Health Appointment: {therapist_name} <> {client_name}",
                start_time=start_time,
                duration_minutes=duration,
                location=join_url,
                description=calendar_description,
                organizer_email=therapist_email,
                attendee_email=client_email,
            )

            # Create Google Calendar event
            # create_gcalendar_event(
            #     calendar_id=client_email,  # Using client's email as their calendar ID
            #     summary=f"Sol Health Appointment: {therapist_name} <> {client_name}",
            #     start_time=start_time,
            #     duration_minutes=duration,
            #     location=join_url,
            #     description=calendar_description,
            #     organizer_email=therapist_email,
            #     attendee_email=client_email,
            # )

            # Create calendar attachment
            calendar_part = MIMEBase("text", "calendar")
            calendar_part.set_param("method", "REQUEST")
            calendar_part.set_param("charset", "UTF-8")
            calendar_part.set_param("component", "VEVENT")
            calendar_part.set_param("name", "event.ics")
            calendar_part.set_payload(ics_content)
            encoders.encode_base64(calendar_part)

            msg.attach(calendar_part)

            # Send email
            self.ses_client.send_raw_email(
                Source=msg["From"],
                Destinations=[client_email],
                RawMessage={"Data": msg.as_string()},
            )

            logger.info(
                "Email sent successfully",
                extra={"to": client_email, "from": therapist_email},
            )
            return True

        except ClientError as e:
            logger.error(
                "Failed to send email",
                extra={"args": str(e), "to": client_email, "from": therapist_email},
            )
            return False
