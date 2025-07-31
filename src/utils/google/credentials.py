import os
import boto3
import json # <-- Add this import
from google.oauth2 import service_account
from src.utils.settings import settings # <-- Add this import

_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

def get_credentials():
    """
    Get Google Calendar credentials from AWS Secrets Manager.
    """
    secret_name = settings.GOOGLE_CALENDAR_SECRET_NAME
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        print(f"ERROR: Could not retrieve secret '{secret_name}'.")
        raise e
    
    # Decode the secret string
    secret_string = get_secret_value_response['SecretString']
    credentials_info = json.loads(secret_string)
    
    # Create credentials from the secret's content
    creds = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=_SCOPES
    )
    return creds