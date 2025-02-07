import os

from dotenv import load_dotenv

from src.utils.singletone import Singleton


class Settings(Singleton):
    def __init__(self):
        load_dotenv()
        self.INTAKEQ_AUTH_KEY = os.getenv("INTAKEQ_AUTH_KEY")
        self.INTAKEQ_BASE_URL = os.getenv("INTAKEQ_BASE_URL")
        self.INTAKEQ_SIGNUP_FORM = os.getenv("INTAKEQ_SIGNUP_FORM")

        self.TEST_USER_ID = os.getenv("TEST_USER_ID")
        self.TEST_PRACTITIONER_ID = os.getenv("TEST_PRACTITIONER_ID")

        self.AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

        self.GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")

        self.RDS_HOST = os.getenv("RDS_HOST")
        self.RDS_PORT = os.getenv("RDS_PORT")
        self.RDS_USER = os.getenv("RDS_USER")
        self.RDS_PASSWORD = os.getenv("RDS_PASSWORD")
        self.RDS_DATABASE = os.getenv("RDS_DATABASE")

        self.TEST_S3_MEDIA_ID = os.getenv("TEST_S3_MEDIA_ID")
        self.IS_AWS = os.getenv("IS_AWS").lower() == "true"


settings = Settings()
