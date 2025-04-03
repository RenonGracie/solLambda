from pydantic import BaseModel, UUID4


class ClientSignupQuery(BaseModel):
    response_id: str


class ClientSignup(BaseModel):
    id: UUID4

    response_id: str | None

    first_name: str | None
    last_name: str | None
    email: str | None
    phone: str | None
    gender: str | None
    age: str | None
    state: str | None

    i_would_like_therapist: list[str] | None
    alcohol: str | None
    drugs: str | None

    pleasure_doing_things: str | None
    feeling_down: str | None
    trouble_falling: str | None
    feeling_tired: str | None
    poor_appetite: str | None
    feeling_bad_about_yourself: str | None
    trouble_concentrating: str | None
    moving_or_speaking_so_slowly: str | None
    suicidal_thoughts: str | None

    feeling_nervous: str | None
    not_control_worrying: str | None
    worrying_too_much: str | None
    trouble_relaxing: str | None
    being_so_restless: str | None
    easily_annoyed: str | None
    feeling_afraid: str | None

    university: str | None

    what_brings_you: str | None
    lived_experiences: list[str] | None
    best_time_for_first_session: str | None

    promo_code: str | None
    referred_by: str | None


class ClientSignupForms(BaseModel):
    forms: list[ClientSignup]
