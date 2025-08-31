#!/usr/bin/env python3
import json
from pathlib import Path

from btcmi import runner
import btcmi.io

R = Path(__file__).resolve().parents[1]


def _cmp(nm: str, tmp_path: Path, monkeypatch) -> None:
    data = json.loads((R / f"examples/{nm}.json").read_text())
    out_path = tmp_path / f"{nm}.out.json"
    gold = json.loads((R / f"tests/golden/{nm}.golden.json").read_text())

    seen = {}
    original = btcmi.io.write_output

    def fake_write_output(d, p):
        seen["data"] = d
        seen["path"] = p
        original(d, p)

    monkeypatch.setattr(btcmi.io, "write_output", fake_write_output)

    result = runner.run_v2(data, "2025-01-01T00:00:00Z", out_path=out_path)
    assert result == gold
    assert seen["data"] == result
    assert seen["path"] == out_path
    assert json.loads(out_path.read_text()) == gold


def test_intraday_fractal(tmp_path, monkeypatch):
    _cmp("intraday_fractal", tmp_path, monkeypatch)


def test_swing_fractal(tmp_path, monkeypatch):
    _cmp("swing_fractal", tmp_path, monkeypatch)
