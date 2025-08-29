#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
# Ensure local package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from btcmi.logging_util import log, new_trace_id
from btcmi.schema_util import load_json, validate_json
from btcmi.core.registry import get_engine

def main():
    p=argparse.ArgumentParser(prog="btcmi")
    sub=p.add_subparsers(dest="cmd", required=True)
    pr=sub.add_parser("run", help="Produce BTCMI report from input JSON")
    pr.add_argument("--input", required=True); pr.add_argument("--out", required=True); pr.add_argument("--fixed-ts", dest="fixed_ts"); pr.add_argument("--fractal", action="store_true")
    pv=sub.add_parser("validate", help="Validate JSON against schema"); pv.add_argument("--schema", required=True, type=Path); pv.add_argument("--data", required=True, type=Path)
    args=p.parse_args(); trace=new_trace_id()
    if args.cmd=="run":
        data=load_json(args.input)
        try: validate_json(data, Path(__file__).resolve().parents[1]/"input_schema.json")
        except Exception as e: log("warn","input_schema_validation_failed",trace=trace,error=str(e))
        # If explicit mode present, enforce consistency with --fractal flag
        mode = data.get("mode")
        if mode=="v1" and args.fractal: log("warn","mode_flag_mismatch",trace=trace,mode=mode,fractal_flag=True)
        if mode=="v2.fractal" and not args.fractal: log("warn","mode_flag_mismatch",trace=trace,mode=mode,fractal_flag=False)
        regime = "v2.fractal" if args.fractal or mode=="v2.fractal" else "v1"
        engine = get_engine(regime)
        out = engine(data, args.fixed_ts, args.out)
        try: validate_json(out, Path(__file__).resolve().parents[1]/"output_schema.json")
        except Exception as e: log("error","output_schema_validation_failed",trace=trace,error=str(e)); return 2
        log("info","run_ok",trace=trace,out=args.out,fractal=(regime=="v2.fractal"),overall=out["summary"]["overall_signal"]); return 0
    else:
        data=load_json(args.data); validate_json(data,args.schema); print("OK"); return 0
if __name__=="__main__":
    raise SystemExit(main())
