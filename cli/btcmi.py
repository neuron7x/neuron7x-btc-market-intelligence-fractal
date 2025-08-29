#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import datetime as dt
import sys
import logging
from pathlib import Path
from typing import Dict
# Ensure local package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from btcmi.logging_cfg import configure_logging, new_run_id
from btcmi.schema_util import load_json, validate_json
from btcmi import engine_v1 as v1
from btcmi import engine_v2 as v2

ALLOWED_SCENARIOS = frozenset(v1.SCENARIO_WEIGHTS.keys())

def run_v1(data, fixed_ts, out_path):
    scenario=data.get("scenario")
    if scenario is None:
        raise ValueError("'scenario' field is required")
    if scenario not in ALLOWED_SCENARIOS:
        raise ValueError("'scenario' must be one of: "+", ".join(sorted(ALLOWED_SCENARIOS)))
    window=data.get("window")
    if window is None:
        raise ValueError("'window' field is required")
    feats:Dict[str,float]=data.get("features",{})
    norm=v1.normalize(feats); base,weights,contrib=v1.base_signal(scenario,norm); ng=v1.nagr_score(data.get("nagr_nodes",[])); overall=v1.combine(base,ng)
    exp=set(v1.NORM_SCALE.keys()); comp=len([k for k in feats.keys() if k in exp])/(len(exp) or 1)
    conf=round(0.5+0.5*comp,3); notes=[]; constraints=False
    if comp<0.6: notes.append("low_feature_completeness")
    asof=fixed_ts or dt.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    out={"schema_version":data.get("schema_version","2.0.0"),
         "lineage":data.get("lineage",{}),
         "asof":asof,
         "summary":{"scenario":scenario,"window":window,"overall_signal":round(overall,6),"confidence":conf,"router_path":f"{scenario}/v1","nagr_score":round(ng,6),"advisories":notes},
         "details":{"normalized_features":{k:round(v,6) for k,v in norm.items()},"weights":v1.SCENARIO_WEIGHTS[scenario],"contributions":{k:round(v,6) for k,v in contrib.items()},"constraints_applied":constraints,"diagnostics":{"completeness":round(comp,3),"notes":notes}}}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True); Path(out_path).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out

def run_v2(data, fixed_ts, out_path):
    scenario=data.get("scenario")
    if scenario is None:
        raise ValueError("'scenario' field is required")
    if scenario not in ALLOWED_SCENARIOS:
        raise ValueError("'scenario' must be one of: "+", ".join(sorted(ALLOWED_SCENARIOS)))
    window=data.get("window")
    if window is None:
        raise ValueError("'window' field is required")
    f1=data.get("features_micro",{}); f2=data.get("features_mezo",{}); f3=data.get("features_macro",{})
    vol_pctl=float(data.get("vol_regime_pctl",0.5))
    n1=v2.normalize_layer(f1, v2.SCALES["L1"]); n2=v2.normalize_layer(f2, v2.SCALES["L2"]); n3=v2.normalize_layer(f3, v2.SCALES["L3"])
    w1=v2.layer_equal_weights(n1); w2=v2.layer_equal_weights(n2); w3=v2.layer_equal_weights(n3)
    s1,_=v2.level_signal(n1,w1,data.get("nagr_nodes",[])); s2,_=v2.level_signal(n2,w2,data.get("nagr_nodes",[])); s3,_=v2.level_signal(n3,w3,data.get("nagr_nodes",[]))
    regime, alphas = v2.router_weights(vol_pctl)
    overall=v2.combine_levels(s1,s2,s3,alphas)
    coverage=sum(len(x)>0 for x in [n1,n2,n3])/3.0
    conf=round(0.5+0.5*min(coverage,1.0),3); notes=[]; asof=fixed_ts or dt.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    out={"schema_version":data.get("schema_version","2.0.0"),
         "lineage":data.get("lineage",{}),
         "asof":asof,
         "summary":{"scenario":scenario,"window":window,"overall_signal":round(overall,6),"confidence":conf,"router_path":f"{scenario}/v2.fractal","nagr_score":0.0,"advisories":notes,
                                 "overall_signal_L1":round(s1,6),"overall_signal_L2":round(s2,6),"overall_signal_L3":round(s3,6),"level_weights":alphas},
         "details":{"normalized_micro":{k:round(v,6) for k,v in n1.items()},"normalized_mezo":{k:round(v,6) for k,v in n2.items()},"normalized_macro":{k:round(v,6) for k,v in n3.items()},"router_regime":regime,
                    "diagnostics":{"completeness":round(coverage,3),"notes":notes}}}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True); Path(out_path).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out

def main():
    configure_logging(); logger=logging.getLogger(__name__)
    p=argparse.ArgumentParser(prog="btcmi")
    sub=p.add_subparsers(dest="cmd", required=True)
    pr=sub.add_parser("run", help="Produce BTCMI report from input JSON")
    pr.add_argument("--input", required=True); pr.add_argument("--out", required=True); pr.add_argument("--fixed-ts", dest="fixed_ts"); pr.add_argument("--fractal", action="store_true")
    pv=sub.add_parser("validate", help="Validate JSON against schema"); pv.add_argument("--schema", required=True, type=Path); pv.add_argument("--data", required=True, type=Path)
    args=p.parse_args(); run_id=new_run_id()
    if args.cmd=="run":
        data=load_json(args.input)
        try:
            validate_json(data, Path(__file__).resolve().parents[1]/"input_schema.json")
        except Exception:
            logger.warning("input_schema_validation_failed", extra={"run_id": run_id})
        # If explicit mode present, enforce consistency with --fractal flag
        mode = data.get("mode")
        if mode=="v1" and args.fractal:
            logger.warning("mode_flag_mismatch", extra={"run_id": run_id, "mode": mode})
        if mode=="v2.fractal" and not args.fractal:
            logger.warning("mode_flag_mismatch", extra={"run_id": run_id, "mode": mode})
        out = run_v2(data, args.fixed_ts, args.out) if args.fractal or mode=="v2.fractal" else run_v1(data, args.fixed_ts, args.out)
        try:
            validate_json(out, Path(__file__).resolve().parents[1]/"output_schema.json")
        except Exception:
            logger.error("output_schema_validation_failed", extra={"run_id": run_id, "mode": mode}); return 2
        logger.info("run_ok", extra={"run_id": run_id, "mode": "v2.fractal" if (args.fractal or mode=='v2.fractal') else "v1"}); return 0
    else:
        data=load_json(args.data); validate_json(data,args.schema); print("OK"); return 0
if __name__=="__main__":
    raise SystemExit(main())
