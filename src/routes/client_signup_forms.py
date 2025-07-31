# src/routes/client_signup_forms.py
from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag
from flask_openapi3 import APIBlueprint, Tag

from src.db.database import db
from src.models.api.base import Email
from src.models.api.client_signup import ClientSignup as SignupForm
from src.models.api.client_signup import ClientSignupQuery
from src.models.api.client_signup import ClientSignup as SignupForm
from src.models.api.client_signup import ClientSignupQuery
from src.models.api.error import Error
from src.models.db.signup_form import ClientSignup

__tag = Tag(name="Clients Signup Forms")
client_signup_api = APIBlueprint(
    "clients_signup",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/clients_signup",
)


@client_signup_api.get("", responses={200: SignupForm, 404: Error}, summary="Search clients")
def search_clients(query: ClientSignupQuery):
    form = db.query(ClientSignup).filter_by(response_id=query.response_id).first()
    if form:
        data = SignupForm(**form.__dict__)
        data.therapist_specializes_in = form.therapist_specializes_in
        data.lived_experiences = form.lived_experiences
        data.utm = form.utm
        data.payment_type = form.payment_type
        return jsonify(data.dict()), 200


@client_signup_api.get(
    "all", responses={200: SignupForm, 404: Error}, summary="Search clients"
)
def all_clients(query: Email):
    forms = db.query(ClientSignup).filter_by(email=query.email).all()
    items = []
    for form in forms:
        data = SignupForm(**form.__dict__)
        data.therapist_specializes_in = form.therapist_specializes_in
        data.lived_experiences = form.lived_experiences
        
        # Handle payment_type with fallback for staging environments
        try:
            data.payment_type = getattr(form, 'payment_type', 'out_of_pocket')
        except AttributeError:
            # Fallback for environments where payment_type doesn't exist yet
            data.payment_type = 'out_of_pocket'
            
        items.append(data.dict())
    return jsonify({"forms": items}), 200