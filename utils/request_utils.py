import requests

from models.clients import Client
from utils.settings import settings

def save_update_client(client: Client):
    if settings.TEST_USER_ID:
        client.ClientId = settings.TEST_USER_ID
    if settings.TEST_PRACTITIONER_ID:
        client.PractitionerId = settings.TEST_PRACTITIONER_ID
    return requests.post(url=settings.INTAKEQ_BASE_URL+"/clients",headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, data=client.dict())

def search_clients(args: dict):
    return requests.get(url=settings.INTAKEQ_BASE_URL+"/clients",headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, params=args)

def add_client_tag(data: dict):
    return requests.post(url=settings.INTAKEQ_BASE_URL+"/clientTags",headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, data=data)

def delete_client_tag(args: dict):
    return requests.delete(url=settings.INTAKEQ_BASE_URL+"/clientTags",headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY}, params=args)

def client_diagnoses(client_id: int):
    return requests.get(url=f"{settings.INTAKEQ_BASE_URL}/client/{client_id}/diagnoses",headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY})