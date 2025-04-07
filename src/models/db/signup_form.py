import json
from uuid import uuid4

import emoji
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.utils.typeform.typeform_parser import TypeformData, TypeformIds
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
    __tablename__ = "signup_forms"

    id = Column("id", UUID, primary_key=True, default=uuid4)

    response_id = Column("response_id", String(50), unique=True)

    first_name = Column("first_name", Text)
    last_name = Column("last_name", Text)
    email = Column("email", Text)
    phone = Column("phone", String(50))
    gender = Column("gender", String(20))
    age = Column("age", String(20))
    state = Column("state", String(100))
    race = Column("race", String(100))

    _therapist_specializes_in = Column("therapist_specializes_in", Text)
    therapist_identifies_as = Column("therapist_identifies_as", String(50))

    alcohol = Column("alcohol", String(50))
    drugs = Column("drugs", String(50))

    pleasure_doing_things = Column("pleasure_doing_things", String(50))
    feeling_down = Column("feeling_down", String(50))
    trouble_falling = Column("trouble_falling", String(50))
    feeling_tired = Column("feeling_tired", String(50))
    poor_appetite = Column("poor_appetite", String(50))
    feeling_bad_about_yourself = Column("feeling_bad_about_yourself", String(50))
    trouble_concentrating = Column("trouble_concentrating", String(50))
    moving_or_speaking_so_slowly = Column("moving_or_speaking_so_slowly", String(50))
    suicidal_thoughts = Column("suicidal_thoughts", String(50))

    feeling_nervous = Column("feeling_nervous", String(50))
    not_control_worrying = Column("not_control_worrying", String(50))
    worrying_too_much = Column("worrying_too_much", String(50))
    trouble_relaxing = Column("trouble_relaxing", String(50))
    being_so_restless = Column("being_so_restless", String(50))
    easily_annoyed = Column("easily_annoyed", String(50))
    feeling_afraid = Column("feeling_afraid", String(50))

    university = Column("university", Text)

    _lived_experiences = Column("lived_experiences", Text)

    promo_code = Column("promo_code", String(255))
    referred_by = Column("referred_by", Text)

    _how_did_you_hear_about_us = Column("how_did_you_hear_about_us", Text)

    _utm = Column("utm_params", Text, nullable=True)

    @property
    def therapist_specializes_in(self):
        return json.loads(self._therapist_specializes_in or "[]")

    @therapist_specializes_in.setter
    def therapist_specializes_in(self, data):
        self._therapist_specializes_in = json.dumps(data)

    @property
    def lived_experiences(self):
        return json.loads(self._lived_experiences or "[]")

    @lived_experiences.setter
    def lived_experiences(self, experiences):
        self._lived_experiences = json.dumps(experiences)

    @property
    def how_did_you_hear(self):
        return json.loads(self._how_did_you_hear_about_us or "[]")

    @how_did_you_hear.setter
    def how_did_you_hear(self, sources):
        self._how_did_you_hear_about_us = json.dumps(sources)

    @property
    def utm(self) -> dict:
        return json.loads(self._utm or "{}")

    @utm.setter
    def utm(self, sources: dict):
        self._utm = json.dumps(sources)

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

    @property
    def suicidal_thoughts_points(self):
        return _calc_points(self.suicidal_thoughts)


def create_from_typeform_data(response_id: str, data: TypeformData) -> ClientSignup:
    client = ClientSignup()
    client.response_id = response_id

    client.first_name = data.get_value(TypeformIds.FIRST_NAME)
    client.last_name = data.get_value(TypeformIds.LAST_NAME)
    client.phone = data.get_value(TypeformIds.PHONE)
    client.email = data.get_value(TypeformIds.EMAIL)
    client.gender = data.get_value(TypeformIds.GENDER)
    client.age = data.get_value(TypeformIds.AGE)
    client.state = data.get_value(TypeformIds.STATE)
    client.race = data.get_value(TypeformIds.RACE)

    client.university = data.get_value(TypeformIds.UNIVERSITY)

    client.therapist_identifies_as = data.get_value(
        TypeformIds.I_WOULD_LIKE_THERAPIST_IDENTIFIES
    )
    client.therapist_specializes_in = data.get_value(
        TypeformIds.I_WOULD_LIKE_THERAPIST_SPECIALIZES
    )

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

    client.lived_experiences = list(
        map(
            lambda text: emoji.replace_emoji(text),
            data.lived_experiences,
        )
    )

    client.promo_code = data.get_value(TypeformIds.PROMO_CODE)
    client.referred_by = data.get_value(TypeformIds.REFERRED_BY)

    client.how_did_you_hear = data.how_did_you_heard
    return client
