#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
CLI = R / "cli" / "btcmi.py"


def test_v1_intraday():
    out = R / "tests/tmp/intraday_v1.out.json"
    gold = R / "tests/golden/intraday_v1.golden.json"
    r = subprocess.run(
        [
            "python3",
            str(CLI),
            "run",
            "--input",
            str(R / "examples/intraday.json"),
            "--out",
            str(out),
            "--fixed-ts",
            "2025-01-01T00:00:00Z",
        ]
    )
    assert r.returncode == 0
    assert json.loads(out.read_text()) == json.loads(gold.read_text())
