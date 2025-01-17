from flask import Blueprint, jsonify

from models.clients import Client
from utils.flask_utils import api

from flask_pydantic_spec import Request, Response

client_route = Blueprint("clients", __name__)

@client_route.route("")
@api.validate(
    tags=['Clients'],
    resp=Response(HTTP_200=Client),
)
def overview():
    return jsonify(Client().dict()), 200