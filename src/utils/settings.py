import os

from dotenv import load_dotenv

from src.utils.singletone import Singleton


class Settings(Singleton):
    def __init__(self):
        load_dotenv()
        self.INTAKEQ_AUTH_KEY = os.getenv("INTAKEQ_AUTH_KEY")
        self.INTAKEQ_BASE_URL = "https://intakeq.com/api/v1"
        self.INTAKEQ_SIGNUP_FORM = os.getenv("INTAKEQ_SIGNUP_FORM")

        self.TEST_USER_ID = os.getenv("TEST_USER_ID")
        self.TEST_PRACTITIONER_ID = os.getenv("TEST_PRACTITIONER_ID")

        self.AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

        self.RDS_HOST = os.getenv("RDS_HOST")
        self.RDS_PORT = os.getenv("RDS_PORT")
        self.RDS_USER = os.getenv("RDS_USER")
        self.RDS_PASSWORD = os.getenv("RDS_PASSWORD")
        self.RDS_DATABASE = os.getenv("RDS_DATABASE")
        self.RDS_INSTANCE_IDENTIFIER = os.getenv("RDS_INSTANCE_IDENTIFIER")

        self.TEST_THERAPIST_EMAIL = os.getenv("TEST_THERAPIST_EMAIL")
        self.IS_AWS = os.getenv("IS_AWS", "false").lower() == "true"

        self.ANALYTICS_MEASUREMENT_ID = os.getenv("ANALYTICS_MEASUREMENT_ID")
        self.ANALYTICS_API_SECRET = os.getenv("ANALYTICS_API_SECRET")

        self.AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
        self.AIRTABLE_TABLE_ID = os.getenv("AIRTABLE_TABLE_ID")

        self.TEST_WELCOME_VIDEO = os.getenv("TEST_WELCOME_VIDEO")
        self.TEST_GREETINGS_VIDEO = os.getenv("TEST_GREETINGS_VIDEO")

        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

        self.SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
        self.BOT_URL = "https://intakeq-bot-482066738827.us-central1.run.app"


settings = Settings()
