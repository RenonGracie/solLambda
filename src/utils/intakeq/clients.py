from src.utils.logger import get_logger
from src.utils.request_utils import save_update_client, search_clients

logger = get_logger()


def search_client(email: str, name: str, *, payment_type: str | None = None) -> dict | None:
    client = None

    def find_client(clients) -> dict | None:
        if len(clients) > 0:
            try:
                return next(
                    item
                    for item in clients
                    if str(item["Email"]).lower() == email.lower()
                    and str(item["Name"]).strip().lower() == name.lower().strip()
                )
            except StopIteration:
                return None
        else:
            return None

    logger.debug("Searching clients", extra={"email": email})
    kwargs = {"payment_type": payment_type} if payment_type else {}
    result = search_clients({"search": email, "includeProfile": True}, **kwargs)
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
        kwargs = {"payment_type": payment_type} if payment_type else {}
        result = search_clients({"search": name, "includeProfile": True}, **kwargs)
        if result.status_code != 200:
            logger.debug(
                "Search result",
                extra={"response": result.json(), "status": result.status_code},
            )
        else:
            client = find_client(result.json())
    logger.debug("Client search result", extra={"found": client is not None})

    return client


def reassign_client(client: dict, therapist_id: str, *, payment_type: str | None = None):
    """
    Transfer client to another therapist.
    If client already has a therapist, use transfer_client_data API.
    If client has no therapist, simply assign the new therapist.
    """
    try:
        if client.get("PractitionerId") == therapist_id:
            return
        client["PractitionerId"] = therapist_id
        kwargs = {"payment_type": payment_type} if payment_type else {}
        save_update_client(client, **kwargs)
    except Exception as e:
        logger.error("Client search error", extra={"error": str(e)})
