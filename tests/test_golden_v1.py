#!/usr/bin/env python3
import json
from pathlib import Path

from btcmi import runner

R = Path(__file__).resolve().parents[1]


def test_v1_intraday(tmp_path, monkeypatch):
    data = json.loads((R / "examples/intraday.json").read_text())
    out_path = tmp_path / "intraday_v1.out.json"
    gold = json.loads((R / "tests/golden/intraday_v1.golden.json").read_text())

    seen = {}
    original = runner.write_output

    def fake_write_output(d, p):
        seen["data"] = d
        seen["path"] = p
        original(d, p)

    monkeypatch.setattr(runner, "write_output", fake_write_output)

    result = runner.run_v1(data, "2025-01-01T00:00:00Z", out_path=out_path)
    assert result == gold
    assert seen["data"] == result
    assert seen["path"] == out_path
    assert json.loads(out_path.read_text()) == gold
