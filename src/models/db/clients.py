import enum
from uuid import uuid4

import emoji
from sqlalchemy import Column, String, UUID, ARRAY, Enum
from sqlalchemy.orm import mapped_column

from src.utils.typeform_utils import TypeformData, TypeformIds
from src.models.db.base import Base


class QuestionAnswer(str, enum.Enum):
    not_at_all = "Not at all"
    several_days = "Several days"
    more_than_half_the_days = "More than half the days"
    nearly_every_day = "Nearly every day"

    @property
    def points(self):
        match self:
            case QuestionAnswer.not_at_all:
                return 0
            case QuestionAnswer.several_days:
                return 1
            case QuestionAnswer.more_than_half_the_days:
                return 2
            case QuestionAnswer.nearly_every_day:
                return 3


class ClientSignup(Base):
    __tablename__ = "clients"

    id = Column(UUID, primary_key=True, index=True, default=uuid4)

    response_id = Column(String, index=True)

    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    gender = Column(String)
    age = Column(String)
    state = Column(String)

    i_would_like_therapist = Column(ARRAY(String))
    alcohol = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    drugs = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )

    pleasure_doing_things = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    feeling_down = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    trouble_falling = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    feeling_tired = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    poor_appetite = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    feeling_bad_about_yourself = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    trouble_concentrating = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    moving_or_speaking_so_slowly = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    suicidal_thoughts = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )

    feeling_nervous = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    not_control_worrying = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    worrying_too_much = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    trouble_relaxing = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    being_so_restless = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    easily_annoyed = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )
    feeling_afraid = mapped_column(
        Enum(QuestionAnswer), default=QuestionAnswer.not_at_all, nullable=False
    )

    university = Column(String)

    what_brings_you = Column(String)
    lived_experiences = Column(ARRAY(String))
    best_time_for_first_session = Column(String)

    how_did_you_hear_about_us = Column(ARRAY(String))
    promo_code = Column(String)
    referred_by = Column(String)

    @property
    def ph9_sum(self):
        return sum(
            [
                self.pleasure_doing_things.points,
                self.feeling_down.points,
                self.trouble_falling.points,
                self.feeling_tired.points,
                self.poor_appetite.points,
                self.feeling_bad_about_yourself.points,
                self.trouble_concentrating.points,
                self.moving_or_speaking_so_slowly.points,
            ]
        )

    @property
    def gad7_sum(self):
        return sum(
            [
                self.feeling_nervous.points,
                self.not_control_worrying.points,
                self.worrying_too_much.points,
                self.trouble_relaxing.points,
                self.being_so_restless.points,
                self.easily_annoyed.points,
                self.feeling_afraid.points,
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
