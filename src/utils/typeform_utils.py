class TypeformIds:
    FIRST_NAME = "bAU4PM5izLPw"
    LAST_NAME = "QyQGh22FFp7C"
    PHONE = "v9zXJ6bgbebE"
    EMAIL = "mmy8ZN4ZsGBF"

    AGE = "DfxcVIryt3wc"

    STATE = "fC8U7U3cJQFL"

    I_WOULD_LIKE_THERAPIST_SPECIALIZES = "CVL5z059lufX"
    I_WOULD_LIKE_THERAPIST_IDENTIFIES = "ecBOrzCGUhvJ"
    LIVED_EXPERIENCES = "0167KDGBLslw"

    ALCOHOL = "8WplwzBjKVSb"
    DRUGS = "82oHc9iy7Pmh"

    PLEASURE_DOING_THINGS = "M04nbKJncd9M"
    FEELING_DOWN = "h0F37G0sqXxP"
    TROUBLE_FALLING = "uRnwdU1H6ekJ"
    FEELING_TIRED = "N7CIrE5K0M2L"
    POOR_APPETITE = "g8IOdge0N8FB"
    FEELING_BAD_ABOUT_YOURSELF = "kSKbsRYNPRxJ"
    TROUBLE_CONCENTRATING = "3wj9XleHfoTG"
    MOVING_OR_SPEAKING_SO_SLOWLY = "35kvZkl7kMLT"
    SUICIDAL_THOUGHTS = "lzpnX6vNtaXw"

    FEELING_NERVOUS = "ORbVCZxFbKGq"
    NOT_CONTROL_WORRYING = "BbXZFZTqjqnA"
    WORRYING_TOO_MUCH = "3pgnd68OOFd2"
    TROUBLE_RELAXING = "r5g62WEJmTVc"
    BEING_SO_RESTLESS = "PCGU4N2tP2VY"
    EASILY_ANNOYED = "KiYOqFtfrD1m"
    FEELING_AFRAID = "a8q7iIVHwp3P"

    PROMO_CODE = "ktGmxlKsXqFI"


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
