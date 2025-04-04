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
        specializes_value = self.get_value(
            TypeformIds.I_WOULD_LIKE_THERAPIST_SPECIALIZES, auto_join=False
        )
        identifies_value = self.get_value(
            TypeformIds.I_WOULD_LIKE_THERAPIST_IDENTIFIES, auto_join=False
        )

        value = _value_to_list(specializes_value) + list(
            map(
                lambda gender: gender.replace("Male", "Is male").replace(
                    "Female", "Is female"
                ),
                _value_to_list(identifies_value),
            )
        )
        return ",".join(value) if self._use_join and isinstance(value, list) else value

    @property
    def lived_experiences(self):
        family_value = self.get_value(
            TypeformIds.LIVED_EXPERIENCES_FAMILY, auto_join=False
        )
        upbringing_value = self.get_value(
            TypeformIds.LIVED_EXPERIENCES_UPBRINGING, auto_join=False
        )
        identity_value = self.get_value(
            TypeformIds.LIVED_EXPERIENCES_IDENTITY, auto_join=False
        )

        value = (
            _value_to_list(family_value)
            + _value_to_list(upbringing_value)
            + _value_to_list(identity_value)
        )
        return ",".join(value) if self._use_join and isinstance(value, list) else value

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

    def get_value(self, field_name: str, auto_join: bool | None = None):
        join = auto_join if auto_join is not None else self._use_join
        answer = self._data.get(field_name)
        if not answer:
            return ""
        value = self._get_value_from_typeform(self._data.get(field_name))
        return ",".join(value) if join and isinstance(value, list) else value
