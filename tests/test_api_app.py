import json
import importlib.resources
from pathlib import Path

from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client.parser import text_string_to_metric_families

from btcmi.api import app, load_runners, REQUEST_COUNTER

f = importlib.resources.files("btcmi")


def _load_example(name: str) -> dict:
    return json.loads(f.joinpath(f"examples/{name}.json").read_text())


def test_run_success():
    client = TestClient(app)
    payload = _load_example("intraday")
    resp = client.post("/run", json=payload)
    assert resp.status_code == 200
    assert "summary" in resp.json()


def test_run_invalid_payload():
    client = TestClient(app)
    resp = client.post("/run", json={"mode": "v1"})
    assert resp.status_code == 422


def test_run_unknown_mode():
    client = TestClient(app)
    payload = _load_example("intraday")
    payload["mode"] = "foo"
    resp = client.post("/run", json=payload)
    assert resp.status_code == 400
    assert "unknown mode" in resp.json()["detail"]


def test_run_runner_exception(monkeypatch):
    def bad_runner(*args, **kwargs):  # pragma: no cover
        raise RuntimeError("boom")

    monkeypatch.setitem(load_runners(), "v1", bad_runner)
    client = TestClient(app)
    payload = _load_example("intraday")
    resp = client.post("/run", json=payload)
    assert resp.status_code == 500


def test_run_out_path_none(monkeypatch):
    seen = {}

    def runner(p, _t, *, out_path: str | Path | None = None):
        seen["out_path"] = out_path
        return {
            "schema_version": "2.0.0",
            "lineage": {},
            "summary": {"scenario": "intraday", "window": "1h"},
            "details": {},
            "asof": "1970-01-01T00:00:00Z",
        }

    monkeypatch.setitem(load_runners(), "v1", runner)
    client = TestClient(app)
    payload = _load_example("intraday")
    resp = client.post("/run", json=payload)
    assert resp.status_code == 200
    assert seen["out_path"] is None


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
