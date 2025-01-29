import os

from dotenv import load_dotenv

from utils.singletone import Singleton

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


settings = Settings()