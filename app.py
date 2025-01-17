from flask import jsonify, request, make_response
from flask_pydantic_spec import Response

from models.clients import Client
from routes.clients import client_route
from utils.flask_utils import app, api
from utils.request_utils import save_update_client
from utils.typeform_utils import get_intake_client

app.register_blueprint(client_route, url_prefix="/clients")

@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

@app.route('/hook', methods=['POST'])
@api.validate(
    tags=['Webhook'],
    resp=Response(HTTP_200=Client),
)
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