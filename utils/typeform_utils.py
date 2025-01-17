from models.clients import Client

class __TypeformIds:
    FIRST_NAME = "Bcd3yhtVV8qA"
    LAST_NAME = "91kMGKU8j2CH"
    PHONE = "b9DkubXQl2D3"
    EMAIL = "0aZPHNSS2AEa"
    GENDER = "clAn8i6OQOI3"
    STATE = "3AQyhzE0XBx5"

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

def get_intake_client(data: dict) -> Client:
    client = Client()
    phone = __get_value(data.get(__TypeformIds.PHONE))
    if phone:
        phone = phone[1:]
    client.FirstName = __get_value(data.get(__TypeformIds.FIRST_NAME))
    client.LastName = __get_value(data.get(__TypeformIds.LAST_NAME))
    client.Name = f"{client.FirstName} {client.LastName}"
    client.Phone = phone
    client.MobilePhone = phone
    client.Email = __get_value(data.get(__TypeformIds.EMAIL))
    client.Gender = __get_value(data.get(__TypeformIds.GENDER))
    client.StateShort = __get_value(data.get(__TypeformIds.STATE))
    return client