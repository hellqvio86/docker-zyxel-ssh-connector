import json
import logging
import os
from typing import Any


class JSONFormatter(logging.Formatter):
    """Simple JSON formatter for logging records."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "file": record.pathname,
            "line": record.lineno,
            "message": record.getMessage(),
            "host": getattr(record, "host", "unknown"),
            "command": getattr(record, "command", "unknown"),
        }

        if hasattr(record, "output"):
            log_record["output"] = record.output

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def setup_logging(debug: bool = False) -> None:
    """Configure logging to file if debug is enabled."""
    # Check env var if flag not explicitly set
    if not debug:
        debug = os.getenv("DEBUG", "0").lower() in ("1", "true", "yes", "on")

    if not debug:
        return

    logger = logging.getLogger("zyxel_cli")
    logger.setLevel(logging.DEBUG)

    # Setup console logging, we will be a container
    handler = logging.StreamHandler()
    formatter = JSONFormatter()
    handler.setFormatter(formatter)

    # Remove existing handlers to avoid duplicates if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(handler)
