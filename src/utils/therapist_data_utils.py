from datetime import timedelta, datetime

from dateutil.rrule import rrulestr

from src.models.api.therapist_s3 import S3MediaType
from src.models.api.therapists import Therapist
from src.models.db.therapists import AppointmentModel
from src.utils import s3
from src.utils.settings import settings


def _rearrange_elements(elements, indices):
    selected_elements = [elements[i] for i in indices if i < len(elements)]
    remaining_elements = [
        elem for idx, elem in enumerate(elements) if idx not in indices
    ]
    rearranged_elements = selected_elements + remaining_elements
    return rearranged_elements


def _find_client_age_group(client_age):
    if 20 <= client_age <= 26:
        return "Early/Mid 20s"
    elif 27 <= client_age <= 29:
        return "Late 20s"
    elif 30 <= client_age <= 39:
        return "30s"
    elif 40 <= client_age <= 49:
        return "40s"
    elif 50 <= client_age <= 59:
        return "50s"
    elif client_age >= 60:
        return "60+"
    else:
        return "Age out of range"


def implement_age_factor(age_str: str, matched: list[dict]) -> list[dict]:
    try:
        age = int(age_str)
        suitable = []
        for i in range(len(matched)):
            data = matched[i]
            if str(data["therapist"].age).__eq__(_find_client_age_group(age)):
                suitable.append(i)
                if len(suitable) >= 3:
                    break

        if len(suitable):
            matched = _rearrange_elements(matched, suitable)

        return matched
    except ValueError:
        return matched


def load_therapist_media(data: dict) -> dict:
    therapist = data["therapist"]
    email = (
        settings.TEST_THERAPIST_EMAIL
        if settings.TEST_THERAPIST_EMAIL
        else therapist.email
    )
    therapist.welcome_video_link = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.WELCOME_VIDEO
    )
    therapist.image_link = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.IMAGE
    )
    data["therapist"] = therapist.dict()
    return data


def provide_therapist_slots(
    therapist: Therapist,
    first_week_appointments: list[AppointmentModel] | None,
    second_week_appointments: list[AppointmentModel] | None,
) -> Therapist:
    first_week_slots = []
    second_week_slots = []
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if first_week_appointments is not None or second_week_appointments is not None:
        for i in range(168):
            if first_week_appointments:
                first_week_slots.append(now + timedelta(hours=i))
            if second_week_appointments:
                second_week_slots.append(now + timedelta(hours=i, days=7))

    def _filter_slots(slot: datetime, appointments: AppointmentModel, duration) -> bool:
        if appointments.recurrence:
            for rec in appointments.recurrence:
                rrule = rrulestr(rec, dtstart=appointments.start_date)
                for dt in rrule.between(
                    slot + timedelta(days=-1), slot + duration + timedelta(days=1)
                ):
                    if (
                        dt.astimezone()
                        <= slot.astimezone()
                        < dt.astimezone() + duration
                    ):
                        return True
            return False
        else:
            return False

    def filter_slots(
        slots: list[datetime], appointments: list[AppointmentModel]
    ) -> list[datetime]:
        return list(
            filter(
                lambda dt: not any(
                    appointment.start_date.astimezone()
                    <= dt.astimezone()
                    <= appointment.end_date.astimezone()
                    or _filter_slots(
                        dt, appointment, appointment.end_date - appointment.start_date
                    )
                    for appointment in appointments
                ),
                slots,
            )
        )

    therapist.available_slots = []
    if first_week_appointments:
        therapist.available_slots += filter_slots(
            first_week_slots, first_week_appointments
        )
    if second_week_appointments:
        therapist.available_slots += filter_slots(
            second_week_slots, second_week_appointments
        )
    return therapist
