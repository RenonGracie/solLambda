from flask import jsonify, request
from flask_openapi3 import Tag, Info, OpenAPI

from models.clients import Client
from routes.clients import client_api
from utils.request_utils import save_update_client
from utils.typeform_utils import get_intake_client

__jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
__security_schemes = {"jwt": __jwt}

info = Info(title="SolHealth API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=__security_schemes)

app.register_api(client_api)

@app.post('/hook', tags=[Tag(name="Webhook")], responses={200: Client},)
def typeform_webhook():
    print(request)
    response_json = request.get_json()
    questions_json = response_json['form_response']['definition']['fields']
    questions = dict(map(lambda item: (item['ref'], item), questions_json))
    answers = response_json['form_response']['answers']
    json: dict = {}
    for answer in answers:
        question = questions[answer['field']['ref']]
        json[question['id']] = {
            'ref': answer['field']['ref'],
            'answer': answer[answer['type']] if answer['type'] != 'multiple_choice' else answer['choices'],
            'title': question['title'],
            'type': question['type']
        }
    client = get_intake_client(json)
    result = save_update_client(client)
    print(result)
    return jsonify(result.json()), result.status_code


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)