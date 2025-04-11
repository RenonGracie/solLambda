import logging
from pyairtable import Api

from src.utils.settings import settings
from src.utils.therapists.airtable import save_therapists
from src.models.api.therapists import Therapist

logger = logging.getLogger(__name__)


def update_therapists_table():
    """
    Updates the therapists table by fetching data from Airtable and saving it to the database.
    This function will be called on a schedule every 3 hours.
    """
    try:
        logger.info("Starting therapists table update")

        # Initialize Airtable API
        api = Api(settings.AIRTABLE_API_KEY)
        table = api.table(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_ID)

        # Get all therapists from Airtable
        therapists = list(
            map(lambda therapist: Therapist(therapist).dict(), table.all())
        )

        # Save therapists to the database
        save_therapists(therapists)

        logger.info(
            f"Therapists table successfully updated. Processed {len(therapists)} records."
        )
        return {
            "success": True,
            "message": f"Updated {len(therapists)} therapist records",
        }
    except Exception as e:
        logger.error(f"Error updating therapists table: {str(e)}")
        return {"success": False, "error": str(e)}
