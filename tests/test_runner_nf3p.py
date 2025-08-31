import json
from pathlib import Path

import pytest

from btcmi import runner

R = Path(__file__).resolve().parents[1]


def _load_data():
    data = json.loads((R / "examples/intraday_fractal.json").read_text())
    data["mode"] = "v2.nf3p"
    return data


def test_run_nf3p_round_trip(tmp_path, monkeypatch):
    data = _load_data()
    out_file = tmp_path / "out.json"

    seen = {}
    original = runner.write_output

    def fake_write_output(d, p):
        seen["data"] = d
        seen["path"] = p
        original(d, p)

    monkeypatch.setattr(runner, "write_output", fake_write_output)

    result = runner.run_nf3p(data, "2024-01-01T00:00:00Z", out_file)
    assert "predictions" in result
    assert "backtest" in result
    assert seen["data"] == result
    assert seen["path"] == out_file
    saved = json.loads(out_file.read_text())
    assert saved == result
    assert result["asof"] == "2024-01-01T00:00:00Z"
    assert result["predictions"]["L1"] == pytest.approx(0.475329)
    assert result["backtest"]["mse"] == pytest.approx(0.09825, rel=1e-4)
