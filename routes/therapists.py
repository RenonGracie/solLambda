from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint
from pyairtable import Api

from models.client_match import MatchedTherapists, ClientMatchData, MatchQuery
from models.therapists import TherapistsTable
from utils.matching_algorithm import match_client_with_therapists
from utils.settings import settings

__tag = Tag(name="Therapists")
therapist_api = APIBlueprint("therapists", __name__, abp_tags=[__tag], abp_security=[{"jwt": []}], url_prefix="/therapists")

api = Api(settings.AIRTABLE_API_KEY)
table = api.table('appeJMQ59lRzIADPP', 'tblpLJff9xwTB54yd')

@therapist_api.get("", responses={200: TherapistsTable}, summary="Get therapists table")
def get_therapists():
    return jsonify({"table" : table.all()}), 200


@therapist_api.post("/match", responses={200: MatchedTherapists}, summary="Get therapists table")
def match(body: ClientMatchData, query: MatchQuery):
    matched = match_client_with_therapists(body.model_dump(), table.all(), query.limit)
    return jsonify({"matched" : matched}), 200