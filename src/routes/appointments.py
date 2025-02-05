from flask import jsonify
from flask_openapi3 import Tag, APIBlueprint

from src.models.api.appointments import (
    BookingSettings,
    Appointments,
    Appointment,
    AppointmentQuery,
    AppointmentPath,
    AppointmentsShort,
    CancelAppointment,
)
from src.utils.request_utils import (
    get_booking_settings,
    search_appointments,
    get_appointment,
    create_appointment,
    update_appointment,
    appointment_cancellation,
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
    "/settings", responses={200: BookingSettings}, summary="Get booking settings"
)
def get_settings():
    result = get_booking_settings()
    return jsonify(result.json()), result.status_code


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
def new_appointment(body: AppointmentsShort):
    result = create_appointment(body.dict())
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
