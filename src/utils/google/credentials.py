import os
from google.oauth2 import service_account

_SCOPES = [
    "https://www.googleapis.com/auth/calendar",  # Full calendar access
    "https://www.googleapis.com/auth/calendar.events",  # Event creation
]
_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "google_credentials.json")


def get_credentials():
    """
    Get Google Calendar credentials using service account with optional domain-wide delegation

    Args:
        subject_email: Email of the user to impersonate (for domain-wide delegation)
                      If None, uses service account directly

    Returns:
        Credentials object or None if credentials are not available
    """
    creds = service_account.Credentials.from_service_account_file(
        _CREDENTIALS_FILE, scopes=_SCOPES
    )
    return creds
