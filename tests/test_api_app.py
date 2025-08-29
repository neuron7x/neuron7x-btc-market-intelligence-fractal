import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app import app, RUNNERS

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
