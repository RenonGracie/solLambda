import json

import requests

from src.models.api.clients import Client
from src.utils.settings import settings


def _intakeq_get(path: str, params: dict = None):
    return requests.get(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY},
        params=params,
    )


def _intakeq_delete(path: str, params: dict = None):
    return requests.delete(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY},
        params=params,
    )


def _intakeq_post(path: str, data: dict):
    return requests.post(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY},
        json=data,
    )


def _intakeq_put(path: str, data: dict):
    return requests.put(
        url=settings.INTAKEQ_BASE_URL + path,
        headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY},
        json=data,
    )


def save_update_client(client: Client):
    if settings.TEST_USER_ID:
        client.ClientId = settings.TEST_USER_ID
    if settings.TEST_PRACTITIONER_ID:
        client.PractitionerId = settings.TEST_PRACTITIONER_ID
    return _intakeq_post("/clients", data=client.dict())


def search_clients(args: dict):
    return _intakeq_get("/clients", params=args)


def add_client_tag(data: dict):
    return _intakeq_post("/clientTags", data=data)


def delete_client_tag(args: dict):
    return _intakeq_delete("/clientTags", params=args)


def client_diagnoses(client_id: str):
    return _intakeq_get(f"/client/{client_id}/diagnoses")


def get_booking_settings():
    return _intakeq_get("/appointments/settings")


def search_appointments(args: dict):
    return _intakeq_get("/appointments", params=args)


def get_appointment(appointment_id: str):
    return _intakeq_get(
        f"/appointments/{appointment_id}",
    )


def create_appointment(data: dict):
    return _intakeq_post("/appointments", data)


def update_appointment(data: dict):
    return _intakeq_put("/appointments", data)


def appointment_cancellation(data: dict):
    return _intakeq_post("/appointments/cancellation", data)


def intakeq(data: dict):
    try:
        return requests.post(
            url="https://intakeq-bot-g5xg5czqfa-uc.a.run.app",
            headers={
                "X-Auth-Key": settings.INTAKEQ_AUTH_KEY,
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
        json=json.dumps(data),
    )
