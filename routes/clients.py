from flask import Blueprint, jsonify, request

from models.clients import *
from utils.flask_utils import api

from flask_pydantic_spec import Request, Response

from utils.request_utils import save_update_client, search_clients as search, add_client_tag, delete_client_tag, client_diagnoses

client_route = Blueprint("clients", __name__)

@client_route.route("", methods=["PATCH"])
@api.validate(
    body=Request(Client),
    tags=['Clients'],
    resp=Response(HTTP_200=Client),
)
def update_client():
    request_json = request.get_json()
    client = Client(**request_json)
    result = save_update_client(client)
    return jsonify(result.json()), result.status_code


@client_route.route("search", methods=["GET"])
@api.validate(
    query=ClientQueryModel,
    tags=['Clients'],
    resp=Response(HTTP_200=Clients),
)
def search_clients():
    args = request.args
    result = search(args)
    return jsonify({"clients": result.json()}), result.status_code


@client_route.route("clientTags", methods=["POST"])
@api.validate(
    query=ClientTagQuery,
    body=Request(ClientTag),
    tags=['Clients'],
    resp=Response(HTTP_204=None),
)
def add_tag():
    result = add_client_tag(request.get_json())
    return '', result.status_code


@client_route.route("clientTags", methods=["DELETE"])
@api.validate(
    query=ClientTagQuery,
    tags=['Clients'],
    resp=Response(HTTP_204=None),
)
def delete_tag():
    result = delete_client_tag(request.args)
    return '', result.status_code


@client_route.route("/client/<int:client_id>/diagnoses", methods=["GET"])
@api.validate(
    tags=['Clients'],
    resp=Response(HTTP_200=ClientDiagnoses),
)
def get_client_diagnoses(client_id):
    result = client_diagnoses(client_id)
    return jsonify({"diagnoses": result.json()}), result.status_code