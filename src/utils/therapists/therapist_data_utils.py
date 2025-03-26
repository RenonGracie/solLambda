from datetime import timedelta, datetime

from dateutil.rrule import rrulestr
from zoneinfo import ZoneInfo

from src.models.api.therapist_s3 import S3MediaType
from src.models.api.therapist_videos import VideoType
from src.models.db.therapist_videos import TherapistVideoModel
from src.models.db.therapists import AppointmentModel
from src.utils import s3
from src.utils.settings import settings


_DEFAULT_ZONE = ZoneInfo("US/Eastern")


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


def load_therapist_media(db, data: dict) -> dict:
    therapist = data["therapist"]
    email = (
        settings.TEST_THERAPIST_EMAIL
        if settings.TEST_THERAPIST_EMAIL
        else therapist.email
    )
    videos = db.query(TherapistVideoModel).filter_by(email=email).all()
    for video in videos:
        if video.type == VideoType.WELCOME.value:
            therapist.welcome_video_link = video.video_url
        if video.type == VideoType.GREETING.value:
            therapist.greetings_video_link = video.video_url

    if not therapist.welcome_video_link and settings.TEST_WELCOME_VIDEO:
        therapist.welcome_video_link = settings.TEST_WELCOME_VIDEO
    if not therapist.greetings_video_link and settings.TEST_GREETINGS_VIDEO:
        therapist.greetings_video_link = settings.TEST_GREETINGS_VIDEO

    therapist.image_link = s3.get_media_url(
        user_id=email, s3_media_type=S3MediaType.IMAGE
    )
    data["therapist"] = therapist.dict()
    return data


def provide_therapist_slots(
    first_week_appointments: list[AppointmentModel] | None,
    second_week_appointments: list[AppointmentModel] | None,
) -> list[datetime]:
    first_week_slots = []
    second_week_slots = []
    now = datetime.now(tz=_DEFAULT_ZONE).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    if first_week_appointments is not None or second_week_appointments is not None:
        for day in range(7):
            for hour in range(15):
                if first_week_appointments is not None:
                    first_week_slots.append(now + timedelta(hours=hour, days=day))
                if second_week_appointments is not None:
                    second_week_slots.append(now + timedelta(hours=hour, days=day + 7))

    def _check_slot(slot: datetime, start: datetime, end: datetime) -> bool:
        start = start.astimezone()
        slot = slot.astimezone()
        end = end.astimezone()
        if start <= slot < end:
            return True
        if start <= slot + timedelta(minutes=45) < end:
            return True
        return False

    def filter_slots(
        slots: list[datetime], appointments: set[AppointmentModel]
    ) -> list[datetime]:
        filtered = slots
        for appointment in appointments:
            recurrence = appointment.recurrence
            start = appointment.start
            if recurrence is None or len(recurrence) == 0:
                end = appointment.end
                filtered = [dt for dt in filtered if not _check_slot(dt, start, end)]
            else:
                duration = appointment.end - start
                for rule_str in recurrence:
                    print(rule_str, start, start.tzinfo is None)
                    if start.tzinfo is None:
                        occurrences = rrulestr(rule_str, dtstart=start).between(
                            now.replace(tzinfo=None),
                            now.replace(tzinfo=None) + duration + timedelta(days=15),
                        )
                    else:
                        occurrences = rrulestr(rule_str, dtstart=start).between(
                            now.astimezone(),
                            now.astimezone() + duration + timedelta(days=15),
                        )
                    for occurrence_start in occurrences:
                        occurrence_end = occurrence_start + duration
                        filtered = [
                            dt
                            for dt in filtered
                            if not _check_slot(dt, occurrence_start, occurrence_end)
                        ]

        return filtered

    available_slots = filter_slots(
        first_week_slots + second_week_slots,
        set((first_week_appointments or []) + (second_week_appointments or [])),
    )
    return available_slots
