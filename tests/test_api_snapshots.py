import json
import os
from pathlib import Path

R = Path(__file__).resolve().parents[1]

from fastapi.testclient import TestClient

from api.app import app, RUNNERS
from cli.btcmi import run_v1, run_v2

def _load_example(name: str) -> dict:
    return json.loads((R / "examples" / f"{name}.json").read_text())

def _prepare_client(monkeypatch) -> TestClient:
    monkeypatch.setitem(RUNNERS, "v1", lambda p, _t, o: run_v1(p, "2025-01-01T00:00:00Z", o))
    monkeypatch.setitem(RUNNERS, "v2.fractal", lambda p, _t, o: run_v2(p, "2025-01-01T00:00:00Z", o))
    return TestClient(app)

def _assert_snapshot(client: TestClient, payload: dict, golden: Path) -> None:
    resp = client.post("/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    if os.getenv("UPDATE_SNAPSHOTS"):
        golden.write_text(json.dumps(data, indent=2))
    assert data == json.loads(golden.read_text())

def test_run_v1_snapshot(monkeypatch):
    client = _prepare_client(monkeypatch)
    payload = _load_example("intraday")
    _assert_snapshot(client, payload, R / "tests/golden/api_run_v1.golden.json")

def test_run_v2_snapshot(monkeypatch):
    client = _prepare_client(monkeypatch)
    payload = _load_example("intraday_fractal")
    _assert_snapshot(client, payload, R / "tests/golden/api_run_v2.golden.json")
