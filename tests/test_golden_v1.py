#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]; CLI=R/"cli"/"btcmi.py"
def test_v1_intraday():
    out=R/"tests/tmp/intraday_v1.out.json"; gold=R/"tests/golden/intraday_v1.golden.json"
    r=subprocess.run(["python3",str(CLI),"run","--input",str(R/"examples/intraday.json"),"--out",str(out),"--fixed-ts","2025-01-01T00:00:00Z"])
    assert r.returncode==0
    got=json.loads(out.read_text()); exp=json.loads(gold.read_text())
    for o in (got, exp):
        o["audit"]["ts_start"]=0
        o["audit"]["ts_end"]=0
        o["audit"]["trace_id"]="trace"
    assert got==exp
