#!/usr/bin/env python3
import json
import subprocess
import sys
import importlib.resources
from pathlib import Path

R = Path(__file__).resolve().parents[1]
f = importlib.resources.files("btcmi")
CLI = "cli.btcmi"


def test_drift_guard_mid():
    out1 = R / "tests/tmp/dg_v1.out.json"
    r1 = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(f.joinpath("examples/intraday.json")),
            "--out",
            str(out1),
            "--fixed-ts",
            "2025-01-01T00:00:00Z",
            "--mode",
            "v1",
        ]
    )
    assert r1.returncode == 0
    s1 = json.loads(out1.read_text())["summary"]["overall_signal"]
    sample = {
        "schema_version": "2.0.0",
        "lineage": {"request_id": "1234567890abcdef1234567890abcdef"},
        "scenario": "intraday",
        "window": "1h",
        "mode": "v2.fractal",
        "features_micro": {
            "price_change_pct": 0.8,
            "volume_change_pct": 35.0,
            "funding_rate_bps": 4.0,
            "oi_change_pct": 12.0,
        },
        "features_mezo": {},
        "features_macro": {},
        "vol_regime_pctl": 0.55,
    }
    inp = R / "tests/tmp/dg_v2.in.json"
    inp.write_text(json.dumps(sample), encoding="utf-8")
    out2 = R / "tests/tmp/dg_v2.out.json"
    r2 = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(inp),
            "--out",
            str(out2),
            "--fixed-ts",
            "2025-01-01T00:00:00Z",
            "--mode",
            "v2.fractal",
        ]
    )
    assert r2.returncode == 0
    s2 = json.loads(out2.read_text())["summary"]["overall_signal"]
    assert abs(s2 - s1) <= 0.25
