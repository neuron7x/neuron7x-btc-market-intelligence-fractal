import json
import logging
import os
import sys
import time
import uuid

try:
    from opentelemetry import trace
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        OTLPSpanExporter,
    )
except Exception:  # pragma: no cover - opentelemetry is optional
    trace = None
    LoggingInstrumentor = None
    TracerProvider = None
    BatchSpanProcessor = None
    ConsoleSpanExporter = None
    OTLPSpanExporter = None

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
        if trace is not None:
            span = trace.get_current_span()
            ctx = span.get_span_context()
            if ctx.is_valid:
                rec["trace_id"] = f"{ctx.trace_id:032x}"
                rec["span_id"] = f"{ctx.span_id:016x}"
        return json.dumps(rec, ensure_ascii=False)

def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    if LoggingInstrumentor is not None:
        LoggingInstrumentor().instrument(set_logging_format=False)

    if TracerProvider is not None and BatchSpanProcessor is not None:
        exporter_name = os.getenv("OTEL_EXPORTER", "console").lower()
        if exporter_name == "otlp" and OTLPSpanExporter is not None:
            exporter = OTLPSpanExporter()
        else:
            exporter = ConsoleSpanExporter()
        provider = TracerProvider(resource=Resource.create({"service.name": "btcmi"}))
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

def new_run_id() -> str:
    return uuid.uuid4().hex
