import logging
import os
import sys
import uuid

from pythonjsonlogger import jsonlogger


class JSONFormatter(jsonlogger.JsonFormatter):
    """Format log records as structured JSON."""

    def add_fields(self, log_record, record, message_dict):  # noqa: D401, ANN001
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)
        log_record["ts"] = int(record.created * 1000)
        log_record["level"] = record.levelname.lower()
        # The base formatter uses the "message" key; rename to "msg"
        log_record["msg"] = log_record.pop("message", record.getMessage())
        log_record["run_id"] = getattr(record, "run_id", None)
        log_record["mode"] = getattr(record, "mode", None)
        log_record["scenario"] = getattr(record, "scenario", None)


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]


def new_run_id() -> str:
    return uuid.uuid4().hex

