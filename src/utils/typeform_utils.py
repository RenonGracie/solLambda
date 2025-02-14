class TypeformIds:
    FIRST_NAME = "ZpNE6gPlqimL"
    LAST_NAME = "i6Vq0HOOoCFA"
    PHONE = "O2RRFNhyN0ki"
    EMAIL = "2rcVFVb8w9LK"

    GENDER = "enJruAtdreAz"

    AGE = "YU4dLIkFJG4T"

    UNIVERSITY = "i8SZCoPAlFlc"

    STATE = "4LLiLAhMSw1x"

    I_WOULD_LIKE_THERAPIST_SPECIALIZES = "n3S63NHiJbeJ"
    I_WOULD_LIKE_THERAPIST_IDENTIFIES = "9MPRbZZPOYb7"
    LIVED_EXPERIENCES = "cubaKBWqjmOu"

    ALCOHOL = "x1gIHnYJItDd"
    DRUGS = "nH69SitRHMj1"

    PLEASURE_DOING_THINGS = "nyrbO2sbPxpM"
    FEELING_DOWN = "p6Ru9DWpDGQA"
    TROUBLE_FALLING = "qZOAuSGkzZJa"
    FEELING_TIRED = "GFz6NgYEsaON"
    POOR_APPETITE = "rXcqXMa2zvZ3"
    FEELING_BAD_ABOUT_YOURSELF = "ZvZWiv2rhyUG"
    TROUBLE_CONCENTRATING = "fYW5AClinzxf"
    MOVING_OR_SPEAKING_SO_SLOWLY = "qFEJeO59PQNa"
    SUICIDAL_THOUGHTS = "6s24QQNgk4RB"

    FEELING_NERVOUS = "WzwDGj9h5zSb"
    NOT_CONTROL_WORRYING = "7Uu6sezExQWc"
    WORRYING_TOO_MUCH = "wMZ1xHx3hO9Q"
    TROUBLE_RELAXING = "EzWLlvgbKOMH"
    BEING_SO_RESTLESS = "nOLsTJkvKSeO"
    EASILY_ANNOYED = "AynrL5fyp8Vg"
    FEELING_AFRAID = "79jEf0ZznNTa"

    PROMO_CODE = "ZHpfkvOOrSyQ"


class TypeformData:
    _data: dict = {}
    _use_join = False

    @property
    def first_name(self):
        return self.get_value(TypeformIds.FIRST_NAME)

    @property
    def last_name(self):
        return self.get_value(TypeformIds.LAST_NAME)

    @property
    def email(self):
        return self.get_value(TypeformIds.EMAIL)

    def __init__(self, data: dict) -> None:
        self._data = data

    def enable_join(self):
        self._use_join = True

    @property
    def i_would_like_therapist(self):
        specializes = self.get_value(TypeformIds.I_WOULD_LIKE_THERAPIST_SPECIALIZES)
        identifies = self.get_value(TypeformIds.I_WOULD_LIKE_THERAPIST_IDENTIFIES)
        if isinstance(specializes, str) and isinstance(identifies, str):
            return f"{specializes}, {identifies.replace('Male', 'Is male').replace('Female', 'Is female')}"
        elif isinstance(specializes, list) and isinstance(identifies, list):
            return specializes + list(
                map(
                    lambda gender: f"Is {gender.lower()}",
                    identifies,
                )
            )
        else:
            return None

    @staticmethod
    def _get_value_from_typeform(data: dict):
        if not data.get("answer"):
            return ""

        match data["type"]:
            case "multiple_choice":
                if data["answer"].get("labels"):
                    return data["answer"].get("labels")
                else:
                    return data["answer"].get("label")
            case "dropdown":
                return data["answer"].get("label")
            case _:
                return data.get("answer")

    def get_value(self, field_name: str):
        answer = self._data.get(field_name)
        if not answer:
            return ""
        value = self._get_value_from_typeform(self._data.get(field_name))
        return ", ".join(value) if self._use_join and isinstance(value, list) else value
