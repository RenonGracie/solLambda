from flask_pydantic_spec import FlaskPydanticSpec

from flask import Flask

from utils.singletone import Singleton

class __FlaskUtils(Singleton):
    def __init__(self):
        self.app = Flask(__name__)

        self.api = FlaskPydanticSpec('flask', title='SolHealth API')
        self.api.register(self.app)

flask = __FlaskUtils()
app = flask.app
api = flask.api