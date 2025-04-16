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


def setup_logger(app):
    """Setup application logging"""
    # Remove default handlers
    app.logger.handlers = []

    # Create console handler
    console_handler = logging.StreamHandler()

    formatter = ConsoleFormatter()
    console_handler.setFormatter(formatter)

    # Add handler to the logger
    app.logger.addHandler(console_handler)

    # Set log level based on environment
    app.logger.setLevel(logging.DEBUG)

    # Disable werkzeug default logger in production
    if settings.ENV != "dev":
        logging.getLogger("werkzeug").setLevel(logging.ERROR)

    return app.logger


# Create a function to add request ID to all requests
def add_request_id():
    """Add request ID to all requests"""
    if not hasattr(request, "id"):
        request.id = request.headers.get("X-Request-ID", "")
    return request.id


# Global logger instance
logger = None


def init_logger(app):
    """Initialize global logger"""
    global logger
    logger = setup_logger(app)
    return logger


def get_logger():
    """Get global logger instance"""
    if logger is None:
        raise RuntimeError("Logger not initialized. Call init_logger(app) first")
    return logger
