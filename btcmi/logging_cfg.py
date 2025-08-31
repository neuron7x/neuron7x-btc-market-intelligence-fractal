import json
import logging
import os
import sys
import time
import uuid


class JsonFormatter(logging.Formatter):
    """Format log records as JSON with standard metadata.

    Each record is serialized to JSON with the timestamp (``ts``),
    log level, message, and optional ``run_id``, ``mode`` and
    ``scenario`` fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        rec = {
            "ts": int(time.time() * 1000),
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            "run_id": getattr(record, "run_id", None),
            "mode": getattr(record, "mode", None),
            "scenario": getattr(record, "scenario", None),
        }
        return json.dumps(rec, ensure_ascii=False)


def configure_logging() -> None:
    """Configure root logger to emit JSON-formatted logs to ``stderr``.

    The log level is taken from the ``LOG_LEVEL`` environment variable,
    defaulting to ``INFO`` if not provided.
    """

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Configure Uvicorn's loggers to use the same JSON formatter. Uvicorn
    # reads a module-level ``LOGGING_CONFIG`` during startup; overriding it
    # here ensures server and access logs also emit JSON records.
    try:  # pragma: no cover - defensive; uvicorn should be available
        import uvicorn.config as uvconfig

        uvconfig.LOGGING_CONFIG = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"()": JsonFormatter},
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default"],
                    "level": level_name,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": level_name,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["access"],
                    "level": level_name,
                    "propagate": False,
                },
            },
        }
    except Exception:  # pragma: no cover - uvicorn not installed
        pass


def new_run_id() -> str:
    """Return a unique identifier for the current run."""

    return uuid.uuid4().hex
