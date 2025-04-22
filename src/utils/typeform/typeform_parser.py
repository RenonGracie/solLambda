from src.utils.typeform.typeform_ids import TypeformIds


def _value_to_list(value):
    if isinstance(value, str):
        if value:
            return [value]
        else:
            return []
    else:
        return value


class TypeformData:
    _data: dict = {}
    variables: list[dict] = []

    @property
    def first_name(self):
        return self.get_value(TypeformIds.FIRST_NAME)

    @property
    def last_name(self):
        return self.get_value(TypeformIds.LAST_NAME)

    @property
    def email(self):
        return self.get_value(TypeformIds.EMAIL)

    def __init__(self, data: dict, variables: list[dict] | None) -> None:
        self._data = data
        self.variables = variables or {}

    def get_var(self, var_name: str):
        for var in self.variables:
            if var["key"] == var_name:
                return var[var["type"]]
        return None

    @property
    def lived_experiences(self):
        family_value = self.get_value(TypeformIds.LIVED_EXPERIENCES_FAMILY)
        upbringing_value = self.get_value(TypeformIds.LIVED_EXPERIENCES_UPBRINGING)
        identity_value = self.get_value(TypeformIds.LIVED_EXPERIENCES_IDENTITY)

        value = (
            _value_to_list(family_value)
            + _value_to_list(upbringing_value)
            + _value_to_list(identity_value)
        )
        return value

    @property
    def how_did_you_heard(self):
        value = self.get_value(TypeformIds.HOW_DID_YOU_HEAR_ABOUT)
        return value if isinstance(value, list) else [value]

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
            case "choice":
                return data["answer"].get("label")
            case _:
                return data.get("answer")

    def get_value(self, field_name: str):
        answer = self._data.get(field_name)
        if not answer:
            return ""
        value = self._get_value_from_typeform(self._data.get(field_name))
        return value
