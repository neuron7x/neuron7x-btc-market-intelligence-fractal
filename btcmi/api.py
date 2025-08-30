from __future__ import annotations

from pathlib import Path
import asyncio

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Any, Dict
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from btcmi.enums import Scenario, Window
from btcmi.runner import run_v1, run_v2
from btcmi.schema_util import validate_json

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


class RunRequest(BaseModel):
    scenario: Scenario
    window: Window
    mode: str = "v1"

    class Config:
        extra = "allow"


class Summary(BaseModel):
    scenario: Scenario
    window: Window

    class Config:
        extra = "allow"


class RunResponse(BaseModel):
    schema_version: str
    lineage: Dict[str, str]
    summary: Summary
    details: Dict[str, Any]
    asof: str


class ValidateRequest(BaseModel):
    class Config:
        extra = "allow"


@app.post("/run", response_model=RunResponse)
async def run_endpoint(payload: RunRequest) -> RunResponse:
    data = payload.model_dump()
    mode = data.get("mode", "v1")
    runner = RUNNERS.get(mode)
    if runner is None:
        raise HTTPException(status_code=400, detail=f"unknown mode: {mode}")
    try:
        validate_json(data, SCHEMA_REGISTRY["input"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        # API requests should not leave artifacts on disk; explicitly disable
        # writing the output file.
        result = await asyncio.to_thread(runner, data, None, out_path=None)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="internal error") from exc
    return result


@app.post("/validate/{schema_name}")
async def validate_endpoint(schema_name: str, payload: ValidateRequest):
    schema_path = SCHEMA_REGISTRY.get(schema_name)
    if schema_path is None:
        raise HTTPException(status_code=404, detail="schema not found")
    try:
        validate_json(payload.model_dump(), schema_path)
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
