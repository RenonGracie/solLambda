from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from models.clients import *
from utils.request_utils import save_update_client, search_clients as search, add_client_tag, delete_client_tag, client_diagnoses

__tag = Tag(name="Clients")
client_api = APIBlueprint("clients", __name__, abp_tags=[__tag], abp_security=[{"jwt": []}], url_prefix="/clients")

@client_api.patch("", responses={200: Client}, summary="Update client")
def update_client(body: Client):
    result = save_update_client(body)
    return jsonify(result.json()), result.status_code


@client_api.get("search", responses={200: Clients}, summary="Search clients")
def search_clients(query: ClientQueryModel):
    result = search(query.model_dump())
    if result.status_code != 200:
        return jsonify(result.json()), result.status_code
    return jsonify({"clients": result.json()}), result.status_code


@client_api.post("clientTags", responses={204: None}, summary="Add client tag")
def add_tag(body: ClientTag):
    result = add_client_tag(body.model_dump())
    return '', result.status_code


@client_api.delete("clientTags", responses={204: None}, summary="Delete client tag")
def delete_tag(query: ClientTagQuery):
    result = delete_client_tag(query.model_dump())
    return '', result.status_code


@client_api.get("/<int:client_id>/diagnoses", responses={200: ClientDiagnoses}, summary="Get client's diagnoses")
def get_client_diagnoses(path: ClientPath):
    result = client_diagnoses(path.client_id)
    if result.status_code != 200:
        return jsonify(result.json()), result.status_code
    return jsonify({"diagnoses": result.json()}), result.status_code