from src.routes.appointments import appointment_api
from src.routes.client_signup_forms import client_signup_api
from src.routes.clients import client_api
from src.routes.emails import emails_api
from src.routes.intakeq_forms import intakeq_forms_api
from src.routes.therapists import therapist_api

__all__ = [
    "appointment_api",
    "client_api",
    "client_signup_api",
    "emails_api",
    "intakeq_forms_api",
    "therapist_api",
]
