import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client.parser import text_string_to_metric_families

from api.app import app, RUNNERS, REQUEST_COUNTER

R = Path(__file__).resolve().parents[1]


def _load_example(name: str) -> dict:
    return json.loads((R / "examples" / f"{name}.json").read_text())


def test_run_success():
    client = TestClient(app)
    payload = _load_example("intraday")
    resp = client.post("/run", json=payload)
    assert resp.status_code == 200
    assert "summary" in resp.json()


def test_run_invalid_payload():
    client = TestClient(app)
    resp = client.post("/run", json={"mode": "v1"})
    assert resp.status_code == 400


def test_run_runner_exception(monkeypatch):
    def bad_runner(*args, **kwargs):  # pragma: no cover
        raise RuntimeError("boom")

    monkeypatch.setitem(RUNNERS, "v1", bad_runner)
    client = TestClient(app)
    payload = _load_example("intraday")
    resp = client.post("/run", json=payload)
    assert resp.status_code == 500


def test_validate_input_valid():
    client = TestClient(app)
    payload = _load_example("intraday")
    resp = client.post("/validate/input", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"valid": True}


def test_validate_input_invalid():
    client = TestClient(app)
    resp = client.post("/validate/input", json={"schema_version": "2.0.0"})
    assert resp.status_code == 400


def test_metrics_prometheus_text_and_counters():
    client = TestClient(app)
    base_validate = REQUEST_COUNTER.labels(endpoint="/validate/input")._value.get()

    payload = _load_example("intraday")
    client.post("/validate/input", json=payload)
    client.post("/validate/input", json={"schema_version": "2.0.0"})

    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == CONTENT_TYPE_LATEST

    metrics = {mf.name: mf for mf in text_string_to_metric_families(resp.text)}
    samples = {s.labels["endpoint"]: s.value for s in metrics["btcmi_requests"].samples}

    assert samples["/validate/input"] == base_validate + 2
