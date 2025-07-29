import requests

from src.utils.settings import settings


# ---------------------------------------------------------------------------
# Internal helper to determine which API key to use
# ---------------------------------------------------------------------------


def _resolve_auth_key(auth_key: str | None = None, payment_type: str | None = None):
    """Return the IntakeQ auth key that should be used for this request.

    Priority:
    1. Explicit *auth_key* argument, if provided.
    2. *payment_type* == "insurance" → insurance key (if set, otherwise fallback).
    3. Default primary key.
    """

    if auth_key:
        return auth_key

    if payment_type == "insurance":
        # Use the secondary key when available, else fallback to the primary one
        return settings.INTAKEQ_AUTH_KEY_INSURANCE or settings.INTAKEQ_AUTH_KEY

    return settings.INTAKEQ_AUTH_KEY


# ---------------------------------------------------------------------------
# Low-level HTTP helpers
# ---------------------------------------------------------------------------


def _intakeq_get(path: str, params: dict | None = None, *, auth_key: str | None = None, payment_type: str | None = None):
    return requests.get(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": _resolve_auth_key(auth_key, payment_type)},
        params=params,
    )


def _intakeq_delete(path: str, params: dict | None = None, *, auth_key: str | None = None, payment_type: str | None = None):
    return requests.delete(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": _resolve_auth_key(auth_key, payment_type)},
        params=params,
    )


def _intakeq_post(path: str, data: dict, timeout: int | None = None, *, auth_key: str | None = None, payment_type: str | None = None):
    return requests.post(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": _resolve_auth_key(auth_key, payment_type)},
        json=data,
        timeout=timeout,
    )


def _intakeq_put(path: str, data: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    return requests.put(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": _resolve_auth_key(auth_key, payment_type)},
        json=data,
    )


# ---------------------------------------------------------------------------
# High-level wrappers – now accept the same optional *auth_key* or *payment_type*
# ---------------------------------------------------------------------------


def save_update_client(client: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    if settings.TEST_USER_ID:
        client["ClientId"] = settings.TEST_USER_ID
    if settings.TEST_PRACTITIONER_ID:
        client["PractitionerId"] = settings.TEST_PRACTITIONER_ID
    return _intakeq_post("/clients", data=client, auth_key=auth_key, payment_type=payment_type)


def search_clients(args: dict):
    return _intakeq_get("/clients", params=args)

def search_clients(args: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_get("/clients", params=args, auth_key=auth_key, payment_type=payment_type)


def get_booking_settings(*, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_get("/appointments/settings", auth_key=auth_key, payment_type=payment_type)


def search_appointments(args: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_get("/appointments", params=args, auth_key=auth_key, payment_type=payment_type)


def get_appointment(appointment_id: str, *, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_get(f"/appointments/{appointment_id}", auth_key=auth_key, payment_type=payment_type)


def create_appointment(data: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_post("/appointments", data, auth_key=auth_key, payment_type=payment_type)


def update_appointment(data: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_put("/appointments", data, auth_key=auth_key, payment_type=payment_type)


def appointment_cancellation(data: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_post("/appointments/cancellation", data, auth_key=auth_key, payment_type=payment_type)


def send_intake_form(data: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    return _intakeq_post("/intakes/send", data, auth_key=auth_key, payment_type=payment_type)


def intakeq(data: dict, *, auth_key: str | None = None, payment_type: str | None = None):
    try:
        return requests.post(
            url=settings.BOT_URL,
            headers={
                "X-Auth-Key": _resolve_auth_key(auth_key, payment_type),
                "Content-type": "application/json",
            },
            json=data,
            timeout=1,
        )
    except requests.exceptions.ReadTimeout:
        return None


def sent_analytics_event(data: dict):
    return requests.post(
        url=f"https://www.google-analytics.com/mp/collect?measurement_id={settings.ANALYTICS_MEASUREMENT_ID}&api_secret={settings.ANALYTICS_API_SECRET}",
        headers={
            "Content-type": "application/json",
        },
        json=data,
    )


def transfer_client_data(
    source_practitioner_id: str, destination_practitioner_id: str, client_id: str
):
    """
    Transfer client data between practitioners.

    Args:
        source_practitioner_id: ID of the current practitioner
        destination_practitioner_id: ID of the practitioner to transfer to
        client_id: ID of the client to transfer
    """
    path = f"/practitioners/{source_practitioner_id}/transferData/{destination_practitioner_id}"
    data = {"ClientId": client_id}
    return _intakeq_post(path, data)
