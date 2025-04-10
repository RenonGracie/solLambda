from src.utils.request_utils import search_clients, save_update_client


def search_client(email: str, name: str) -> dict | None:
    client = None

    def find_client(clients) -> dict | None:
        if len(clients) > 0:
            try:
                return next(
                    item
                    for item in clients
                    if str(item["Email"]).lower() == email.lower()
                    and str(item["Name"]).lower() == name.lower()
                )
            except StopIteration:
                return None
        else:
            return None

    print("searching clients", email)
    result = search_clients({"search": email, "includeProfile": True})
    if result.status_code == 200:
        client = find_client(result.json())
    else:
        print(result.json(), result.status_code)

    print("client found", client is not None)
    if not client:
        print("searching clients", name)
        result = search_clients({"search": name, "includeProfile": True})
        if result.status_code != 200:
            print(result.json(), result.status_code)
        else:
            client = find_client(result.json())
    print("client found", client is not None)

    return client


def reassign_client(client: dict, therapist_id: str):
    """
    Transfer client to another therapist.
    If client already has a therapist, use transfer_client_data API.
    If client has no therapist, simply assign the new therapist.
    """
    try:
        if client.get("PractitionerId") == therapist_id:
            return
        else:
            client["PractitionerId"] = therapist_id
            save_update_client(client)
    except Exception as e:
        print(e)
