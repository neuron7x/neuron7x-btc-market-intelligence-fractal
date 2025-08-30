import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from btcmi.api import app
from btcmi.runner import run_v1, run_v2

R = Path(__file__).resolve().parents[1]

FIXED_TS = "2025-01-01T00:00:00Z"


def _load_example(name: str) -> dict:
    return json.loads((R / "examples" / f"{name}.json").read_text())


def _snapshot_runners() -> dict:
    """Return deterministic runner mapping for snapshot tests."""

    def r1(p, _t, *, out_path=None):
        return run_v1(p, FIXED_TS, out_path)

    def r2(p, _t, *, out_path=None):
        return run_v2(p, FIXED_TS, out_path)

    return {"v1": r1, "v2.fractal": r2}


def _prepare_client(monkeypatch) -> TestClient:
    monkeypatch.setattr("btcmi.runner_registry.load_runners", _snapshot_runners)
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
