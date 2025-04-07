from src.models.api.clients import Client
from src.models.db.signup_form import ClientSignup
from src.utils.states_utils import statename_to_abbr
from src.utils.typeform.typeform_parser import TypeformIds, TypeformData


def create_new_form(data: ClientSignup) -> dict:
    return {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "age": data.age,
        "email": data.email,
        "phone": data.phone,
        "gender": data.gender,
        "state": data.state,
        "race": data.race,
        "university": data.university,
        "therapist_specializes_in": data.therapist_specializes_in,
        "therapist_identifies_as": data.therapist_identifies_as,
        "lived_experiences": data.lived_experiences,
        "alcohol": data.alcohol,
        "drugs": data.drugs,
        "pleasure_doing_things": data.pleasure_doing_things,
        "feeling_down": data.feeling_down,
        "trouble_falling": data.trouble_falling,
        "feeling_tired": data.feeling_tired,
        "poor_appetite": data.poor_appetite,
        "feeling_bad_about_yourself": data.feeling_bad_about_yourself,
        "trouble_concentrating": data.trouble_concentrating,
        "moving_or_speaking_so_slowly": data.moving_or_speaking_so_slowly,
        "suicidal_thoughts": data.suicidal_thoughts,
        "feeling_nervous": data.feeling_nervous,
        "not_control_worrying": data.not_control_worrying,
        "worrying_too_much": data.worrying_too_much,
        "trouble_relaxing": data.trouble_relaxing,
        "being_so_restless": data.being_so_restless,
        "easily_annoyed": data.easily_annoyed,
        "feeling_afraid": data.feeling_afraid,
        "promocode": data.promo_code,
        "how_did_you_hear_about": data.how_did_you_hear,
        "referred_by": data.referred_by,
    }


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
