from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from btcmi.schema_util import validate_json
from cli.btcmi import run_v1, run_v2

app = FastAPI()

# Registry mapping modes to runner implementations
RUNNERS = {
    "v1": run_v1,
    "v2.fractal": run_v2,
}

BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_REGISTRY = {
    "input": BASE_DIR / "input_schema.json",
    "output": BASE_DIR / "output_schema.json",
}

REQUEST_COUNTER = Counter("btcmi_requests_total", "Total HTTP requests", ["endpoint"])


@app.middleware("http")
async def count_requests(request, call_next):
    response = await call_next(request)
    REQUEST_COUNTER.labels(endpoint=request.url.path).inc()
    return response


@app.post("/run")
async def run_endpoint(payload: dict):
    mode = payload.get("mode", "v1")
    runner = RUNNERS.get(mode)
    if runner is None:
        raise HTTPException(status_code=400, detail=f"unknown mode: {mode}")
    result = runner(payload, None, "/dev/null")
    return result


@app.post("/validate/{schema_name}")
async def validate_endpoint(schema_name: str, payload: dict):
    schema_path = SCHEMA_REGISTRY.get(schema_name)
    if schema_path is None:
        raise HTTPException(status_code=404, detail="schema not found")
    try:
        validate_json(payload, schema_path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"valid": True}


@app.get("/metrics")
async def metrics() -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
