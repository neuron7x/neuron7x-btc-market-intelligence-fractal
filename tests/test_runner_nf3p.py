import json
from pathlib import Path

import pytest

from btcmi.runner import run_nf3p

R = Path(__file__).resolve().parents[1]


def _load_data():
    data = json.loads((R / "examples/intraday_fractal.json").read_text())
    data["mode"] = "v2.nf3p"
    return data


def test_run_nf3p_round_trip(tmp_path):
    data = _load_data()
    out_file = tmp_path / "out.json"
    result = run_nf3p(data, "2024-01-01T00:00:00Z", out_file)
    assert "predictions" in result
    assert "backtest" in result
    saved = json.loads(out_file.read_text())
    assert saved == result
    assert result["asof"] == "2024-01-01T00:00:00Z"
    assert result["predictions"]["L1"] == pytest.approx(0.475329)
    assert result["backtest"]["mse"] == pytest.approx(0.09825, rel=1e-4)
