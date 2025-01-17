import requests

from models.clients import Client
from utils.settings import settings

def save_update_client(client: Client):
    if settings.TEST_USER_ID:
        client.ClientId = settings.TEST_USER_ID
    return requests.post(url=settings.INTAKEQ_BASE_URL+"/clients",headers={"X-Auth-Key": settings.INTAKEQ_AUTH_KEY},data=client.dict())