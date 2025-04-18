import json
import logging

from flask import request


class ConsoleFormatter(logging.Formatter):
    """Simple console formatter for development"""

    def format(self, record):
        # Basic message format
        message = f"[{record.levelname}] {record.getMessage()}"

        message += f"\n  Module: {record.module}.{record.funcName}:{record.lineno}"

        keys_to_remove = {
            "pathname",
            "processName",
            "relativeCreated",
            "name",
            "module",
            "funcName",
            "levelno",
            "lineno",
            "levelname",
            "args",
            "filename",
            "msecs",
            "thread",
            "threadName",
            "process",
        }
        filtered_dict = {
            k: v
            for k, v in record.__dict__.items()
            if v is not None and k not in keys_to_remove
        }
        message += f"\n  Extra: {json.dumps(filtered_dict, indent=2)}"

        return message


# Create a function to add request ID to all requests
def add_request_id():
    """Add request ID to all requests"""
    if not hasattr(request, "id"):
        request.id = request.headers.get("X-Request-ID", "")
    return request.id


# Global logger instance
logger = None


def get_logger():
    global logger
    """Get global logger instance"""
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create console handler with formatting
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(ConsoleFormatter())
            logger.addHandler(console_handler)
    return logger
