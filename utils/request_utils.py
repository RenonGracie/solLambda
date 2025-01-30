import requests

from models.clients import Client
from utils.settings import settings

def __get(path: str, params: dict = None):
    return requests.get(url=settings.INTAKEQ_BASE_URL+path,headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, params=params)

def __delete(path: str, params: dict = None):
    return requests.delete(url=settings.INTAKEQ_BASE_URL+path,headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, params=params)

def __post(path: str, data: dict):
    return requests.post(url=settings.INTAKEQ_BASE_URL+path,headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, data=data)

def __put(path: str, data: dict):
    return requests.put(url=settings.INTAKEQ_BASE_URL+path,headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, data=data)

def save_update_client(client: Client):
    if settings.TEST_USER_ID:
        client.ClientId = settings.TEST_USER_ID
    if settings.TEST_PRACTITIONER_ID:
        client.PractitionerId = settings.TEST_PRACTITIONER_ID
    return __post("/clients", data=client.dict())

def search_clients(args: dict):
    return __get("/clients", params=args)

def add_client_tag(data: dict):
    return __post("/clientTags", data=data)

def delete_client_tag(args: dict):
    return __delete("/clientTags", params=args)

def client_diagnoses(client_id: str):
    return __get(f"/client/{client_id}/diagnoses")

def get_booking_settings():
    return __get("/appointments/settings")

def search_appointments(args: dict):
    return __get("/appointments", params=args)

def get_appointment(appointment_id: str):
    return __get(f"/appointments/{appointment_id}",)

def create_appointment(data: dict):
    return __post(f"/appointments", data)

def update_appointment(data: dict):
    return __put("/appointments", data)

def appointment_cancellation(data: dict):
    return __post("/appointments/cancellation", data)

def intakeq(data: dict):
    return requests.post(url="intakeq-bot-g5xg5czqfa-uc.a.run.app",headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, data=data)