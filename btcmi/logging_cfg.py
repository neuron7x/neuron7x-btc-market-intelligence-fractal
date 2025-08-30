import json
import logging
import os
import sys
import time
import uuid

class JsonFormatter(logging.Formatter):
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
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

def new_run_id() -> str:
    return uuid.uuid4().hex
