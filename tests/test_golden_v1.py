#!/usr/bin/env python3
import json
from pathlib import Path

from btcmi.runner import run_v1

R = Path(__file__).resolve().parents[1]


def test_v1_intraday(tmp_path):
    data = json.loads((R / "btcmi/examples/intraday.json").read_text())
    out_path = tmp_path / "intraday_v1.out.json"
    gold = json.loads((R / "tests/golden/intraday_v1.golden.json").read_text())
    result = run_v1(data, "2025-01-01T00:00:00Z", out_path=out_path)
    assert result == gold
    assert json.loads(out_path.read_text()) == gold
