from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

from src.models.api.appointments import (
    Appointment,
    AppointmentPath,
    AppointmentQuery,
    Appointments,
    AppointmentsShort,
    CancelAppointment,
    CreateAppointment,
)
from src.models.api.error import Error
from src.utils.intakeq.booking import (
    book_appointment,
)
from src.utils.request_utils import (
    appointment_cancellation,
    get_appointment,
    search_appointments,
    update_appointment,
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
    responses={200: Appointment, 400: Error, 404: Error, 409: Error, 410: Error},
    summary="Create a new appointment",
)
def new_appointment(body: CreateAppointment):
    return book_appointment(body)


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
