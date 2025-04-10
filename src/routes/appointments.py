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
from src.models.api.base import EmailWithAdminPass
from src.models.api.error import Error
from src.models.db.signup_form import ClientSignup
from src.utils.event_utils import send_ga_event, CALL_SCHEDULED_EVENT, USER_EVENT_TYPE
from src.utils.intakeq.clients import search_client, reassign_client
from src.utils.request_utils import (
    get_booking_settings,
    search_appointments,
    get_appointment,
    create_appointment,
    update_appointment,
    appointment_cancellation,
)
from src.utils.settings import settings
from src.utils.therapists.appointments_utils import delete_all_appointments

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
    "",
    responses={200: Appointment, 400: Error, 404: Error},
    summary="Create a new appointment",
)
def new_appointment(body: CreateAppointment):
    result = get_booking_settings()
    if not result:
        print("Unable to get booking settings")
        return jsonify(Error(error="Unable to get booking settings").dict()), 400
    practitioners = result.json()["Practitioners"]
    try:
        therapist = next(
            item
            for item in practitioners
            if str(item["Email"]).lower() == body.therapist_email.lower()
            or (item["CompleteName"]).lower() == body.therapist_name.lower()
        )
    except StopIteration:
        therapist = None
    if not therapist:
        print("Therapist not found")
        return jsonify(Error(error="Therapist not found").dict()), 404

    form = db.query(ClientSignup).filter_by(response_id=body.client_response_id).first()
    if not form:
        print(f"Signup form with id '{body.client_response_id}' not found")
        return jsonify(
            Error(
                error=f"Signup form with id '{body.client_response_id}' not found"
            ).dict()
        ), 404

    name = f"{form.first_name} {form.last_name}"

    client = search_client(form.email, name)

    if not client:
        print(
            f"Client with name '{form.first_name} {form.last_name}' not found on intakeQ"
        )
        return jsonify(
            Error(
                error=f"Client with name '{form.first_name} {form.last_name}' not found on intakeQ"
            ).dict()
        ), 404
    client_id = client.get("ClientId") or client.get("ClientNumber")

    result = create_appointment(
        {
            "PractitionerId": therapist["Id"],
            "ClientId": client_id,
            "LocationId": "1",
            "UtcDateTime": int(parser.parse(body.datetime).timestamp() * 1000),
            "ServiceId": "e818ad3d-5758-4a7d-a1f9-657af8ac4dc8"
            if form.promo_code and len(form.promo_code) > 1
            else "099e964f-c444-4c68-9668-00f734b95afd",
            "SendClientEmailNotification": body.send_client_email_notification,
            "ReminderType": body.reminder_type if body.reminder_type else "Email",
            "Status": body.status,
        }
    )
    json = result.json()
    if result.status_code == 200:
        send_ga_event(
            client_id=form.utm.get("client_id"),
            name=CALL_SCHEDULED_EVENT,
            value=json.get("Id"),
            user_id=form.utm.get("user_id"),
            session_id=form.utm.get("session_id"),
            event_type=USER_EVENT_TYPE,
            email=form.email,
        )
    reassign_client(client_id, therapist["Id"])
    return jsonify(json), result.status_code


@appointment_api.put(
    "",
    responses={200: Appointment},
    summary="Update an existing appointment",
    doc_ui=False,
)
def update_existing_appointment(body: AppointmentsShort):
    result = update_appointment(body.dict())
    return jsonify(result.json()), result.status_code


@appointment_api.delete(
    "",
    responses={200: Appointment},
    summary="Cancel an existing appointment",
    doc_ui=False,
)
def cancel_appointment(body: CancelAppointment):
    result = appointment_cancellation(body.dict())
    return jsonify(result.json()), result.status_code


@appointment_api.delete(
    "all",
    responses={204: None},
    summary="Delete all appointments by therapist email from db",
)
def delete_therapist_appointments(query: EmailWithAdminPass):
    if not query.admin_password.__eq__(settings.ADMIN_PASSWORD):
        return jsonify({}), 401
    else:
        delete_all_appointments(query.email)
        return jsonify({}), 204
