from models.user import User

class __TypeformIds:
    FIRST_NAME = "Bcd3yhtVV8qA"
    LAST_NAME = "91kMGKU8j2CH"
    PHONE = "b9DkubXQl2D3"
    EMAIL = "0aZPHNSS2AEa"

def __get_value(data: dict):
    match data['type']:
        case 'multiple_choice':
            if data['answer'].get('labels'):
                return data['answer'].get('labels')
            else:
                return data['answer'].get('label')
        case 'dropdown':
            return data['answer']['label']
        case _:
            return data['answer']

def get_intake_user(data: dict) -> User:
    user = User()
    user.Name = __get_value(data.get(__TypeformIds.FIRST_NAME))

    return user