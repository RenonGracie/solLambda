import json
import logging

from src.utils.cron.therapists_update import update_therapists_table

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Lambda function for updating the therapists table on a schedule.
    Called every 3 hours via EventBridge (CloudWatch Events).

    Args:
        event: Event that triggered the function
        context: Lambda execution context

    Returns:
        dict: Function execution result
    """
    logger.info("Starting Lambda function for therapists table update")

    # Call the function to update the therapists table
    result = update_therapists_table()

    logger.info(f"Execution result: {json.dumps(result)}")
    return result
