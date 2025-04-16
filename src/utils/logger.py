import json
import logging

from flask import request

from src.utils.settings import settings


class ConsoleFormatter(logging.Formatter):
    """Simple console formatter for development"""

    def format(self, record):
        # Basic message format
        message = f"[{record.levelname}] {record.getMessage()}"

        message += f"\n  Module: {record.module}.{record.funcName}:{record.lineno}"

        # Add extra fields if present
        if hasattr(record, "extra"):
            message += f"\n  Extra: {json.dumps(record.extra, indent=2)}"

        if hasattr(record, "type"):
            message += f"\n  Type: {record.type}"

        if hasattr(record, "data"):
            message += f"\n  Data: {json.dumps(record.data, indent=2)}"

        # Add exception info if present
        if record.exc_info:
            message += f"\n  Exception: {self.formatException(record.exc_info)}"

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
