from typing import List

from pydantic import BaseModel

from src.models.api.base import CustomField


class AdditionalClient(BaseModel):
    ClientId: str | None
    ClientName: str | None
    ClientEmail: str | None
    ClientPhone: str | None
    IntakeId: str | None


class Appointment(BaseModel):
    EndDateLocal: str | None
    DateCreated: int | None
    LocationName: str | None
    StartDate: int | None
    LastModified: int | None
    FullCancellationReason: str | None
    ClientName: str | None
    EndDateIso: str | None
    StartDateLocalFormatted: str | None
    ClientId: str | None
    StartDateIso: str
    PractitionerName: str | None
    ReminderType: str | None
    Status: str | None
    CreatedBy: str | None
    CancellationDate: str | None
    LocationId: str | None
    Duration: int | None
    PractitionerId: str | None
    ClientEmail: str | None
    EndDate: int | None
    BookedByClient: bool | None
    AdditionalClients: List[AdditionalClient] | None
    CustomFields: List[CustomField] | None
    Price: int | None
    AttendanceConfirmationResponse: str | None
    Id: str | None
    PractitionerEmail: str | None
    StartDateLocal: str | None


class Appointments(BaseModel):
    appointments: List[Appointment] | None


class AppointmentQuery(BaseModel):
    client: int | None = None
    startDate: str | None = None
    endDate: str | None = None
    status: str | None = None
    practitionerEmail: str | None = None
    page: int | None = None
    updatedSince: str | None = None
    deletedOnly: bool | None = None


class AppointmentPath(BaseModel):
    appointment_id: str | None


class AppointmentsShort(BaseModel):
    PractitionerId: str | None
    ClientId: str | None
    ServiceId: str | None
    LocationId: str | None
    Status: str | None
    UtcDateTime: int | None
    SendClientEmailNotification: bool | None
    ReminderType: str | None


class CancelAppointment(BaseModel):
    Reason: str | None
    AppointmentId: str | None


class CreateAppointment(BaseModel):
    client_response_id: str
    therapist_email: str
    is_promo: bool
    datetime: str
    send_client_email_notification: bool
    reminder_type: str | None
    status: str
