from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase

import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart

from src.utils.calendar_utils import create_calendar_event
from src.utils.logger import get_logger
from src.utils.settings import settings

logger = get_logger()


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
        therapist_name: str,
        therapist_email: str,
        client_name: str,
        client_email: str,
        start_time: datetime,
        duration: int = 45,
    ) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Sol Health Appointment"
            msg["From"] = f'"{self.from_name}" <{self.from_email}>'
            msg["To"] = ", ".join([client_email])

            ics_content = create_calendar_event(
                summary=f"Sol Health Appointment: {therapist_name} <> {client_name}",
                start_time=start_time,
                duration_minutes=duration,
                description="<b>Join your Therapy session</b>"
                "<br><br><b>Manage your appointment on contact your Provider</b>"
                "<br>Access your <a href='https://solhealth.intakeq.com/portal'>Client Portal</a> to manage sessions or send messages"
                f"<br>You can also reach your Provider directly <a href='mailto:{therapist_email}'>{therapist_email}</a>"
                "<br><br><b>Cancellation Policy</b>"
                "<br>Please reschedule or cancel your session at least 24 hours in advance to avoid a no-show fee equal to our session cost."
                "<br><br><b>Needs Help?</b>"
                "<br>Email us at <a href='mailto:contact@solhealth.co'>contact@solhealth.co</a>",
                organizer_email=therapist_email,
                attendee_email=client_email,
            )

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
                Source=msg["From"],  # Use the formatted From address
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
