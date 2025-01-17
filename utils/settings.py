import os

from dotenv import load_dotenv

from utils.singletone import Singleton

class Settings(Singleton):
    def __init__(self):
        load_dotenv()
        self.INTAKEQ_AUTH_KEY = os.getenv("INTAKEQ_AUTH_KEY")
        self.INTAKEQ_BASE_URL = os.getenv("INTAKEQ_BASE_URL")
        self.TEST_USER_ID = os.getenv("TEST_USER_ID")

settings = Settings()