from dateutil import parser

from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from src.db.database import db
from src.models.api.appointments import (
    Appointments,
    Appointment,
    AppointmentQuery,
    AppointmentPath,
    AppointmentsShort,
    CancelAppointment,
    CreateAppointment,
)
from src.models.db.clients import ClientSignup
from src.utils.request_utils import (
    get_booking_settings,
    search_appointments,
    get_appointment,
    create_appointment,
    update_appointment,
    appointment_cancellation,
)
from src.utils.request_utils import search_clients

__tag = Tag(name="Appointments")
appointment_api = APIBlueprint(
    "appointments",
    __name__,
    abp_tags=[__tag],
    abp_security=[{"jwt": []}],
    url_prefix="/appointments",
)


@appointment_api.get(
    "", responses={200: Appointments}, summary="Search for existing appointments"
)
def search_all_appointments(query: AppointmentQuery):
    result = search_appointments(query.dict())
    if result.status_code == 200:
        return jsonify({"appointments": result.json()}), result.status_code
    return jsonify(result.json()), result.status_code


@appointment_api.get(
    "/<int:appointment_id>",
    responses={200: Appointment},
    summary="Get an existing appointment",
)
def appointment(path: AppointmentPath):
    result = get_appointment(path.appointment_id)
    return jsonify(result.json()), result.status_code


@appointment_api.post(
    "", responses={200: Appointment}, summary="Create a new appointment"
)
def new_appointment(body: CreateAppointment):
    result = get_booking_settings()
    if not result:
        print("Unable to get booking settings")
        return jsonify({"error": "Unable to get booking settings"}), 400
    practitioners = result.json()["Practitioners"]
    therapist = next(
        item for item in practitioners if item["Email"] == body.therapist_email
    )
    if not therapist:
        print("Therapist not found")
        return jsonify({"error": "Therapist not found"}), 404

    form = db.query(ClientSignup).filter_by(response_id=body.client_response_id).first()
    if not form:
        print(f"Signup form with id '{body.client_response_id}' not found")
        return jsonify(
            {"error": f"Signup form with id '{body.client_response_id}' not found"}
        ), 404
    result = search_clients({"search": form.email})
    if result.status_code != 200:
        return jsonify(result.json()), result.status_code

    clients = result.json()
    client = next(
        item
        for item in clients
        if item["Name"] == f"{form.first_name} {form.last_name}"
    )
    if not client:
        print(
            f"Client with name '{form.first_name} {form.last_name}' not found on intakeQ"
        )
        return jsonify(
            {
                "error": f"Client with name '{form.first_name} {form.last_name}' not found on intakeQ"
            }
        ), 404

    result = create_appointment(
        {
            "PractitionerId": therapist["Id"],
            "ClientId": client["ClientNumber"],
            "LocationId": "1",
            "UtcDateTime": int(parser.parse(body.datetime).timestamp() * 1000),
            "ServiceId": "2a8e50df-b874-430d-9499-eb4b4451249c"
            if body.is_promo
            else "df82b0de-5f6f-4dfa-a3d1-02faf691551c",
            "SendClientEmailNotification": body.send_client_email_notification,
            "ReminderType": body.reminder_type if body.reminder_type else "Email",
            "Status": body.status,
        }
    )
    return jsonify(result.json()), result.status_code


@appointment_api.put(
    "", responses={200: Appointment}, summary="Update an existing appointment"
)
def update_existing_appointment(body: AppointmentsShort):
    result = update_appointment(body.dict())
    return jsonify(result.json()), result.status_code


@appointment_api.delete(
    "", responses={200: Appointment}, summary="Cancel an existing appointment"
)
def cancel_appointment(body: CancelAppointment):
    result = appointment_cancellation(body.dict())
    return jsonify(result.json()), result.status_code
