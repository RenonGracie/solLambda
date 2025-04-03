from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from src.db.database import db
from src.models.api.base import Email
from src.models.api.client_signup import ClientSignup as SignupForm, ClientSignupQuery
from src.models.api.error import Error
from src.models.db.clients import ClientSignup

__tag = Tag(name="Clients Signup Forms")
client_signup_api = APIBlueprint(
    "clients_signup",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/clients_signup",
)


@client_signup_api.get(
    "", responses={200: SignupForm, 404: Error}, summary="Search clients"
)
def search_clients(query: ClientSignupQuery):
    form = db.query(ClientSignup).filter_by(response_id=query.response_id).first()
    if form:
        data = SignupForm(**form.__dict__)
        data.i_would_like_therapist = form.i_would_like_therapist
        data.lived_experiences = form.lived_experiences
        return jsonify(data.dict()), 200
    return jsonify(Error(error="Form not found").dict()), 404


@client_signup_api.get(
    "all", responses={200: SignupForm, 404: Error}, summary="Search clients"
)
def all_clients(query: Email):
    forms = db.query(ClientSignup).filter_by(email=query.email).all()
    items = []
    for form in forms:
        data = SignupForm(**form.__dict__)
        data.i_would_like_therapist = form.i_would_like_therapist
        data.lived_experiences = form.lived_experiences
        items.append(data.dict())
    return jsonify({"forms": items}), 200
