#!/usr/bin/env python3
import json
import importlib.resources
from pathlib import Path

from btcmi.runner import run_v2

R = Path(__file__).resolve().parents[1]
f = importlib.resources.files("btcmi")


def _cmp(nm: str, tmp_path: Path) -> None:
    data = json.loads((f.joinpath(f"examples/{nm}.json")).read_text())
    out_path = tmp_path / f"{nm}.out.json"
    gold = json.loads((R / f"tests/golden/{nm}.golden.json").read_text())
    result = run_v2(data, "2025-01-01T00:00:00Z", out_path=out_path)
    assert result == gold
    assert json.loads(out_path.read_text()) == gold


def test_intraday_fractal(tmp_path):
    _cmp("intraday_fractal", tmp_path)


def test_swing_fractal(tmp_path):
    _cmp("swing_fractal", tmp_path)
