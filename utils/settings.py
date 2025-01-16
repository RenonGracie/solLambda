import os

from dotenv import load_dotenv

from utils.singletone import Singleton

class Settings(Singleton):
    def __init__(self):
        load_dotenv()
        self.INTAKEQ_TOKEN = os.getenv("INTAKEQ_TOKEN")

settings = Settings()