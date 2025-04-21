from flask import jsonify, request
from flask_openapi3 import Tag, APIBlueprint

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
from src.utils.intakeq.booking import (
    book_appointment,
)
from src.utils.request_utils import (
    search_appointments,
    get_appointment,
    update_appointment,
    appointment_cancellation,
)
from src.utils.settings import settings
from src.utils.therapists.appointments_utils import (
    delete_all_appointments,
)

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
    responses={200: Appointment, 400: Error, 404: Error, 409: Error},
    summary="Create a new appointment",
)
def new_appointment(body: CreateAppointment):
    return book_appointment(request.url_root, body)


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
