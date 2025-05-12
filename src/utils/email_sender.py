import re
from datetime import datetime

from src.utils.google.google_calendar import create_gcalendar_event
from src.utils.logger import get_logger

logger = get_logger()


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


def send_invite(
    therapist_name: str,
    therapist_email: str,
    client_name: str,
    client_email: str,
    start_time: datetime,
    telehealth_info: dict | None,
    duration: int = 45,
):
    if telehealth_info:
        invitation_code = extract_invitation_code(telehealth_info["Invitation"])
        join_url = telehealth_info["JoinUrl"]
    else:
        invitation_code = None
        join_url = None

    # Create calendar event without unsubscribe link in description
    calendar_description = (
        "<b>Join your session</b>"
        f"{'<br><br><b>Use the link below to join your scheduled video session:</b>' + f"<br>🔗<a href='{join_url}'>Join Session</a>" + f'<br><br><b>Invitation code:</b> {invitation_code}' if telehealth_info else ''}"
        "<br><br><b>Manage Your Appointment or Contact Your Provider</b>"
        "<br>Access your Client Portal to manage sessions or send messages"
        "<br>🔗<a href='https://solhealth.intakeq.com/portal'>Client Portal</a>"
        f"<br>You can also reach your provider directly at <a href='mailto:{therapist_email}'>{therapist_email}</a>"
        "<br><br><b>Cancellation Policy</b>"
        "<br>Please reschedule or cancel your session at least 24 hours in advance to avoid a no-show fee equal to your session cost."
        "<br><br><b>Needs Help?</b>"
        "<br>Email us at 📩<a href='mailto:contact@solhealth.co'>contact@solhealth.co</a>"
    )

    create_gcalendar_event(
        summary=f"Sol Health Appointment: {therapist_name} <> {client_name}",
        start_time=start_time,
        attendees=[
            {"email": therapist_email, "name": therapist_name},
            {"email": client_email, "name": client_name},
        ],
        description=calendar_description,
        location=join_url,
        duration_minutes=duration,
    )
