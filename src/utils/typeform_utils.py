class TypeformIds:
    FIRST_NAME = "Bcd3yhtVV8qA"
    LAST_NAME = "91kMGKU8j2CH"
    PHONE = "b9DkubXQl2D3"
    EMAIL = "0aZPHNSS2AEa"
    GENDER = "clAn8i6OQOI3"
    AGE = "NFyGjLRsvOQb"
    STATE = "3AQyhzE0XBx5"
    UNIVERSITY = "sHR59ObUeLCw"

    I_WOULD_LIKE_THERAPIST = "B443qff2ZRvs"
    LIVED_EXPERIENCES = "pTMOjbjkbSWL"

    ALCOHOL = "DxXG5npFnjPd"
    DRUGS = "DEC8S8r60O1U"

    PLEASURE_DOING_THINGS = "7kQjFzstcJts"
    FEELING_DOWN = "uUQMfw2xRiQ4"
    TROUBLE_FALLING = "G9LdjqKeO7f4"
    FEELING_TIRED = "YFkgwTszPtMN"
    POOR_APPETITE = "TKA1j8lE6SSd"
    FEELING_BAD_ABOUT_YOURSELF = "TsZ80LFOtbCq"
    TROUBLE_CONCENTRATING = "3SCH6BP1SZWt"
    MOVING_OR_SPEAKING_SO_SLOWLY = "eca2CSO04vLl"
    SUICIDAL_THOUGHTS = "chxgOkME9qj4"

    FEELING_NERVOUS = "B3cxNBp1tpIq"
    NOT_CONTROL_WORRYING = "bvL83C6M9nb1"
    WORRYING_TOO_MUCH = "RdiG8vKXrbVB"
    TROUBLE_RELAXING = "98pYB4y1REbK"
    BEING_SO_RESTLESS = "yVJsRQvXsi1T"
    EASILY_ANNOYED = "QtDBqAbfBRAR"
    FEELING_AFRAID = "1l3TD4JycX7a"

    WHAT_BRINGS_YOU_TO_THERAPY = "RngVovIqApk0"
    BEST_TIME_FOR_FIRST_SESSION = "V7DQU2HoEvfK"
    HOW_DID_YOU_HEAR_ABOUT_US = "ntVzKN7vWQhO"

    REFER = "2mfjCdPxfxVN"
    PROMO_CODE = "gnL63lnuTFLu"


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
