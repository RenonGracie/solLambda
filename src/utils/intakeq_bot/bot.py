from src.utils.typeform_utils import TypeformIds, TypeformData


def create_new_form(data: TypeformData) -> list:
    data.enable_join()
    return [
        True,
        data.get_value(TypeformIds.FIRST_NAME),  # 1
        data.get_value(TypeformIds.LAST_NAME),  # 2
        data.get_value(TypeformIds.PHONE),  # 3
        data.get_value(TypeformIds.EMAIL),  # 4
        data.get_value(TypeformIds.I_WOULD_LIKE_THERAPIST),  # 5
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
        data.get_value(TypeformIds.WHAT_BRINGS_YOU_TO_THERAPY),  # 26
        data.get_value(TypeformIds.AGE),  # 27
        data.get_value(TypeformIds.GENDER),  # 28
        data.get_value(TypeformIds.STATE),  # 29
        data.get_value(TypeformIds.UNIVERSITY),  # 30
        "",  # 31
        data.get_value(TypeformIds.PROMO_CODE),  # 32
        data.get_value(TypeformIds.HOW_DID_YOU_HEAR_ABOUT_US),  # 33
        data.get_value(TypeformIds.REFER),  # 34
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
        data.get_value(TypeformIds.BEST_TIME_FOR_FIRST_SESSION),  # 45
        "",  # 46
        "",  # 47
        data.get_value(TypeformIds.LIVED_EXPERIENCES),  # 48
    ]
