import json

from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from src.db.database import db
from src.models.api.client_form import ClientFormQuery, ClientForms
from src.models.api.clients import ClientShort
from src.models.db.clients import ClientSignup
from src.utils.json_encoder import AlchemyEncoder

__tag = Tag(name="Clients Signup forms")
client_form_api = APIBlueprint(
    "client_forms",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/client_forms",
)


@client_form_api.get("", responses={200: ClientShort}, summary="Get client signup form")
def search_clients(query: ClientFormQuery):
    form = db.query(ClientSignup).filter_by(response_id=query.response_id).first()
    if not form:
        return jsonify({}), 200
    return jsonify(json.loads(json.dumps(form, cls=AlchemyEncoder))), 200


@client_form_api.get(
    "/all",
    responses={200: ClientForms},
    summary="Get all signup form",
)
def get_client_diagnoses():
    forms = db.query(ClientSignup).all()
    return jsonify({"forms": json.loads(json.dumps(forms, cls=AlchemyEncoder))}), 200
