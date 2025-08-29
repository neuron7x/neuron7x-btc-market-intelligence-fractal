#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]; CLI=R/"cli"/"btcmi.py"
def _cmp(nm):
    out=R/f"tests/tmp/{nm}.out.json"; gold=R/f"tests/golden/{nm}.golden.json"
    r=subprocess.run(["python3",str(CLI),"run","--input",str(R/f"examples/{nm}.json"),"--out",str(out),"--fixed-ts","2025-01-01T00:00:00Z","--fractal"])
    assert r.returncode==0
    got=json.loads(out.read_text()); exp=json.loads(gold.read_text())
    for o in (got, exp):
        o["audit"]["ts_start"]=0
        o["audit"]["ts_end"]=0
        o["audit"]["trace_id"]="trace"
    assert got==exp
def test_intraday_fractal(): _cmp("intraday_fractal")
def test_swing_fractal(): _cmp("swing_fractal")
