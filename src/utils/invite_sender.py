import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os

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
    duration: int = 45,
    join_url: str | None = None,
    invitation: str | None = None,
):
    if invitation:
        invitation_code = extract_invitation_code(invitation)
    else:
        invitation_code = None

    # Setup Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("calendar_description.html")

    # Render the template
    calendar_description = template.render(
        {
            "join_url": join_url,
            "invitation_code": invitation_code,
            "therapist_email": therapist_email,
        }
    )

    return create_gcalendar_event(
        summary=f"Sol Health Appointment: {therapist_name} <> {client_name}",
        start_time=start_time,
        attendees=[
            {"email": therapist_email, "name": therapist_name},
            {"email": client_email, "name": client_name},
        ],
        description=calendar_description,
        join_url=join_url,
        duration_minutes=duration,
    )
