from uuid import uuid4

import emoji
from sqlalchemy import Column, String, UUID, ARRAY

from src.utils.typeform_utils import TypeformData, TypeformIds
from src.models.db.base import Base


def _calc_points(value: str):
    match value:
        case "Not at all":
            return 0
        case "Several days":
            return 1
        case "More than half the days":
            return 2
        case "Nearly every day":
            return 3


class ClientSignup(Base):
    __tablename__ = "clients"

    id = Column(UUID, primary_key=True, index=True, default=uuid4)

    response_id = Column(String(50), index=True)

    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    gender = Column(String(20))
    age = Column(String(20))
    state = Column(String(5))

    i_would_like_therapist = Column(ARRAY(String(250)))
    alcohol = Column(String(50))
    drugs = Column(String(50))

    pleasure_doing_things = Column(String(50))
    feeling_down = Column(String(50))
    trouble_falling = Column(String(50))
    feeling_tired = Column(String(50))
    poor_appetite = Column(String(50))
    feeling_bad_about_yourself = Column(String(50))
    trouble_concentrating = Column(String(50))
    moving_or_speaking_so_slowly = Column(String(50))
    suicidal_thoughts = Column(String(50))

    feeling_nervous = Column(String(50))
    not_control_worrying = Column(String(50))
    worrying_too_much = Column(String(50))
    trouble_relaxing = Column(String(50))
    being_so_restless = Column(String(50))
    easily_annoyed = Column(String(50))
    feeling_afraid = Column(String(50))

    university = Column(String(150))

    what_brings_you = Column(String(250))
    lived_experiences = Column(ARRAY(String(250)))
    best_time_for_first_session = Column(String(250))

    how_did_you_hear_about_us = Column(ARRAY(String(100)))
    promo_code = Column(String(100))
    referred_by = Column(String(250))

    @property
    def ph9_sum(self):
        return sum(
            [
                _calc_points(self.pleasure_doing_things),
                _calc_points(self.feeling_down),
                _calc_points(self.trouble_falling),
                _calc_points(self.feeling_tired),
                _calc_points(self.poor_appetite),
                _calc_points(self.feeling_bad_about_yourself),
                _calc_points(self.trouble_concentrating),
                _calc_points(self.moving_or_speaking_so_slowly),
            ]
        )

    @property
    def gad7_sum(self):
        return sum(
            [
                _calc_points(self.feeling_nervous),
                _calc_points(self.not_control_worrying),
                _calc_points(self.worrying_too_much),
                _calc_points(self.trouble_relaxing),
                _calc_points(self.being_so_restless),
                _calc_points(self.easily_annoyed),
                _calc_points(self.feeling_afraid),
            ]
        )


def create_from_typeform_data(response_id: str, data: TypeformData) -> ClientSignup:
    return update_from_typeform_data(response_id, ClientSignup(), data)


def update_from_typeform_data(
    response_id: str, client: ClientSignup, data: TypeformData
) -> ClientSignup:
    client.response_id = response_id

    client.first_name = data.get_value(TypeformIds.FIRST_NAME)
    client.last_name = data.get_value(TypeformIds.LAST_NAME)
    client.email = data.get_value(TypeformIds.EMAIL)
    client.phone = data.get_value(TypeformIds.PHONE)
    client.gender = data.get_value(TypeformIds.GENDER)
    client.age = data.get_value(TypeformIds.AGE)
    client.state = data.get_value(TypeformIds.STATE)

    client.i_would_like_therapist = data.get_value(TypeformIds.I_WOULD_LIKE_THERAPIST)

    client.alcohol = data.get_value(TypeformIds.ALCOHOL)
    client.drugs = data.get_value(TypeformIds.DRUGS)

    client.pleasure_doing_things = data.get_value(TypeformIds.PLEASURE_DOING_THINGS)
    client.feeling_down = data.get_value(TypeformIds.FEELING_DOWN)
    client.trouble_falling = data.get_value(TypeformIds.TROUBLE_FALLING)
    client.feeling_tired = data.get_value(TypeformIds.FEELING_TIRED)
    client.poor_appetite = data.get_value(TypeformIds.POOR_APPETITE)
    client.feeling_bad_about_yourself = data.get_value(
        TypeformIds.FEELING_BAD_ABOUT_YOURSELF
    )
    client.trouble_concentrating = data.get_value(TypeformIds.TROUBLE_CONCENTRATING)
    client.moving_or_speaking_so_slowly = data.get_value(
        TypeformIds.MOVING_OR_SPEAKING_SO_SLOWLY
    )
    client.suicidal_thoughts = data.get_value(TypeformIds.SUICIDAL_THOUGHTS)
    client.feeling_nervous = data.get_value(TypeformIds.FEELING_NERVOUS)
    client.not_control_worrying = data.get_value(TypeformIds.NOT_CONTROL_WORRYING)
    client.worrying_too_much = data.get_value(TypeformIds.WORRYING_TOO_MUCH)
    client.trouble_relaxing = data.get_value(TypeformIds.TROUBLE_RELAXING)
    client.being_so_restless = data.get_value(TypeformIds.BEING_SO_RESTLESS)
    client.easily_annoyed = data.get_value(TypeformIds.EASILY_ANNOYED)
    client.feeling_afraid = data.get_value(TypeformIds.FEELING_AFRAID)

    client.university = data.get_value(TypeformIds.UNIVERSITY)

    client.what_brings_you = data.get_value(TypeformIds.WHAT_BRINGS_YOU_TO_THERAPY)
    client.lived_experiences = list(
        map(
            lambda text: emoji.replace_emoji(text),
            data.get_value(TypeformIds.LIVED_EXPERIENCES),
        )
    )
    client.best_time_for_first_session = data.get_value(
        TypeformIds.BEST_TIME_FOR_FIRST_SESSION
    )

    client.how_did_you_hear_about_us = data.get_value(
        TypeformIds.HOW_DID_YOU_HEAR_ABOUT_US
    )
    client.promo_code = data.get_value(TypeformIds.PROMO_CODE)
    client.referred_by = data.get_value(TypeformIds.REFER)
    return client
