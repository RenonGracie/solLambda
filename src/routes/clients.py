from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

from src.models.api.clients import (
    Client,
    ClientDiagnoses,
    ClientPath,
    ClientQueryModel,
    Clients,
    ClientTag,
    ClientTagQuery,
)
from src.utils.request_utils import (
    add_client_tag,
    client_diagnoses,
    delete_client_tag,
    save_update_client,
)
from src.utils.request_utils import (
    search_clients as search,
)

__tag = Tag(name="Clients")
client_api = APIBlueprint(
    "clients",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/clients",
)


@client_api.get("search", responses={200: Clients}, summary="Search clients")
def search_clients(query: ClientQueryModel):
    result = search(query.dict())
    if result.status_code != 200:
        return jsonify(result.json()), result.status_code
    return jsonify({"clients": result.json()}), result.status_code


@client_api.patch("", responses={200: Client}, summary="Update client", doc_ui=False)
def update_client(body: Client):
    result = save_update_client(body.dict())
    return jsonify(result.json()), result.status_code


@client_api.post(
    "clientTags", responses={204: None}, summary="Add client tag", doc_ui=False
)
def add_tag(body: ClientTag):
    result = add_client_tag(body.dict())
    return "", result.status_code


@client_api.delete(
    "clientTags", responses={204: None}, summary="Delete client tag", doc_ui=False
)
def delete_tag(query: ClientTagQuery):
    result = delete_client_tag(query.dict())
    return "", result.status_code


@client_api.get(
    "/<int:client_id>/diagnoses",
    responses={200: ClientDiagnoses},
    summary="Get client's diagnoses",
)
def get_client_diagnoses(path: ClientPath):
    result = client_diagnoses(path.client_id)
    if result.status_code != 200:
        return jsonify(result.json()), result.status_code
    return jsonify({"diagnoses": result.json()}), result.status_code
