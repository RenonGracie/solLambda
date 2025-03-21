from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from src.models.api.base import Url
from src.models.api.intakeq_forms import IntakeQMandatoryFormQuery
from src.utils.request_utils import send_intake_form

__tag = Tag(name="IntakeQ Forms")
intakeq_forms_api = APIBlueprint(
    "intakeq_forms",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/intakeq_forms",
)


@intakeq_forms_api.post(
    "mandatory_form",
    responses={200: Url},
    summary="Send mandatory form and get its link",
)
def mandatory_form(query: IntakeQMandatoryFormQuery):
    result = send_intake_form(
        {
            "QuestionnaireId": "64c09477f824647fdb9f4c1c",
            "ClientId": query.client_id,
            "PractitionerId": query.therapist_id,
        }
    )
    json = result.json()
    if result.status_code == 200:
        return jsonify(Url(url=json.get("Url")).dict()), result.status_code

    return jsonify(json), result.status_code
