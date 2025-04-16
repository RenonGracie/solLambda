from src.utils.request_utils import search_clients, save_update_client
from src.utils.logger import get_logger

logger = get_logger()


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

    logger.debug("Searching clients", extra={"email": email})
    result = search_clients({"search": email, "includeProfile": True})
    if result.status_code == 200:
        client = find_client(result.json())
    else:
        logger.debug(
            "Search result",
            extra={"response": result.json(), "status": result.status_code},
        )

    logger.debug("Client search result", extra={"found": client is not None})
    if not client:
        logger.debug("Searching clients", extra={"name": name})
        result = search_clients({"search": name, "includeProfile": True})
        if result.status_code != 200:
            logger.debug(
                "Search result",
                extra={"response": result.json(), "status": result.status_code},
            )
        else:
            client = find_client(result.json())
    logger.debug("Client search result", extra={"found": client is not None})

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
        logger.error("Client search error", extra={"error": str(e)})
