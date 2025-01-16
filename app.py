from flask import Flask, jsonify, request, make_response
from flask_pydantic_spec import FlaskPydanticSpec, Request, Response

from models.user import User

app = Flask(__name__)

api = FlaskPydanticSpec('flask', title='Item API')
api.register(app)

@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

@app.route('/hook', methods=['POST'])
@api.validate(
    tags=['Webhook'],
    resp=Response(HTTP_200=User),
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
    return jsonify(User().dict()), 200


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)