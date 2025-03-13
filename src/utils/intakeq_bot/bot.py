from src.models.api.clients import Client
from src.utils.states_utils import statename_to_abbr
from src.utils.typeform.typeform_parser import TypeformIds, TypeformData


def create_new_form(data: TypeformData) -> list:
    data.enable_join()
    return [
        True,
        data.get_value(TypeformIds.FIRST_NAME),  # 1
        data.get_value(TypeformIds.LAST_NAME),  # 2
        data.get_value(TypeformIds.PHONE),  # 3
        data.get_value(TypeformIds.EMAIL),  # 4
        data.i_would_like_therapist,  # 5
        data.get_value(TypeformIds.ALCOHOL),  # 6
        data.get_value(TypeformIds.DRUGS),  # 7
        data.get_value(TypeformIds.PLEASURE_DOING_THINGS),  # 8
        data.get_value(TypeformIds.FEELING_DOWN),  # 9
        data.get_value(TypeformIds.TROUBLE_FALLING),  # 10
        data.get_value(TypeformIds.FEELING_TIRED),  # 11
        data.get_value(TypeformIds.POOR_APPETITE),  # 12
        data.get_value(TypeformIds.FEELING_BAD_ABOUT_YOURSELF),  # 13
        data.get_value(TypeformIds.TROUBLE_CONCENTRATING),  # 14
        data.get_value(TypeformIds.MOVING_OR_SPEAKING_SO_SLOWLY),  # 15
        data.get_value(TypeformIds.SUICIDAL_THOUGHTS),  # 16
        "",  # 17
        data.get_value(TypeformIds.FEELING_NERVOUS),  # 18
        data.get_value(TypeformIds.NOT_CONTROL_WORRYING),  # 19
        data.get_value(TypeformIds.WORRYING_TOO_MUCH),  # 20
        data.get_value(TypeformIds.TROUBLE_RELAXING),  # 21
        data.get_value(TypeformIds.BEING_SO_RESTLESS),  # 22
        data.get_value(TypeformIds.EASILY_ANNOYED),  # 23
        data.get_value(TypeformIds.FEELING_AFRAID),  # 24
        "",  # 25
        "---",  # 26 WHAT_BRINGS_YOU_TO_THERAPY
        data.get_value(TypeformIds.AGE),  # 27 AGE
        data.get_value(TypeformIds.GENDER),  # 28 GENDER
        statename_to_abbr.get(data.get_value(TypeformIds.STATE)),  # 29
        data.get_value(TypeformIds.UNIVERSITY),  # 30 UNIVERSITY
        "",  # 31
        data.get_value(TypeformIds.PROMO_CODE),  # 32
        "Other",  # 33 HOW_DID_YOU_HEAR_ABOUT_US
        "",  # 34 REFERRED BY
        "",  # 35
        "",  # 36
        "",  # 37
        "",  # 38
        "",  # 39
        "",  # 40
        "",  # 41
        "",  # 42
        "",  # 43
        "",  # 44
        "---",  # 45 BEST_TIME_FIRST_SESSION
        "",  # 46
        "",  # 47
        str(data.lived_experiences).replace(
            "🏡 Raised in a non-traditional family",
            "🏡 Grew up in a non-traditional family (e.g. single or divorced parents or foster family)",
        ),  # 48
    ]


def create_client_model(data: TypeformData) -> Client:
    first_name = data.first_name
    last_name = data.last_name

    client = Client()
    client.Name = f"{first_name} {last_name}"
    client.FirstName = first_name
    client.LastName = last_name
    client.Email = data.email
    client.Phone = data.get_value(TypeformIds.PHONE)
    client.Gender = data.get_value(TypeformIds.GENDER)
    client.Archived = False
    client.StateShort = statename_to_abbr.get(data.get_value(TypeformIds.STATE))
    client.Country = "USA"
    return client
