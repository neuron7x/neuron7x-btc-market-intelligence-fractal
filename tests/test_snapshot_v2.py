import json
from pathlib import Path

import pytest

pytest.importorskip("syrupy")

from cli.btcmi import run_v2

R = Path(__file__).resolve().parents[1]


def _run(name: str, tmp_path):
    data = json.loads((R / "examples" / f"{name}.json").read_text())
    return run_v2(data, "2025-01-01T00:00:00Z", tmp_path / "out.json")


def test_intraday_fractal(snapshot, tmp_path):
    out = _run("intraday_fractal", tmp_path)
    assert out == snapshot


def test_swing_fractal(snapshot, tmp_path):
    out = _run("swing_fractal", tmp_path)
    assert out == snapshot

