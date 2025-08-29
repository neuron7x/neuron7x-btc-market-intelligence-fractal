from __future__ import annotations
from typing import Callable, Dict, Any
import json
import datetime as dt
from pathlib import Path

from btcmi import engine_v1 as v1
from btcmi import engine_v2 as v2

EngineFactory = Callable[[Dict[str, Any], str | None, str], Dict[str, Any]]

_REGISTRY: Dict[str, EngineFactory] = {}


def register_engine(regime_id: str, factory: EngineFactory) -> None:
    _REGISTRY[regime_id] = factory


def get_engine(regime_id: str) -> EngineFactory:
    if regime_id not in _REGISTRY:
        raise KeyError(f"unknown regime id: {regime_id}")
    return _REGISTRY[regime_id]


def _run_v1(data: Dict[str, Any], fixed_ts: str | None, out_path: str) -> Dict[str, Any]:
    scenario = data["scenario"]
    window = data["window"]
    feats: Dict[str, float] = data.get("features", {})
    norm = v1.normalize(feats)
    base, weights, contrib = v1.base_signal(scenario, norm)
    ng = v1.nagr_score(data.get("nagr_nodes", []))
    overall = v1.combine(base, ng)
    exp = set(v1.NORM_SCALE.keys())
    comp = len([k for k in feats.keys() if k in exp]) / (len(exp) or 1)
    conf = round(0.5 + 0.5 * comp, 3)
    notes = []
    constraints = False
    if comp < 0.6:
        notes.append("low_feature_completeness")
    asof = fixed_ts or dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    out = {
        "asof": asof,
        "summary": {
            "scenario": scenario,
            "window": window,
            "overall_signal": round(overall, 6),
            "confidence": conf,
            "router_path": f"{scenario}/v1",
            "nagr_score": round(ng, 6),
            "advisories": notes,
        },
        "details": {
            "normalized_features": {k: round(v, 6) for k, v in norm.items()},
            "weights": v1.SCENARIO_WEIGHTS[scenario],
            "contributions": {k: round(v, 6) for k, v in contrib.items()},
            "constraints_applied": constraints,
            "diagnostics": {"completeness": round(comp, 3), "notes": notes},
        },
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def _run_v2(data: Dict[str, Any], fixed_ts: str | None, out_path: str) -> Dict[str, Any]:
    scenario = data["scenario"]
    window = data["window"]
    f1 = data.get("features_micro", {})
    f2 = data.get("features_mezo", {})
    f3 = data.get("features_macro", {})
    vol_pctl = float(data.get("vol_regime_pctl", 0.5))
    n1 = v2.normalize_layer(f1, v2.SCALES["L1"])
    n2 = v2.normalize_layer(f2, v2.SCALES["L2"])
    n3 = v2.normalize_layer(f3, v2.SCALES["L3"])
    w1 = v2.layer_equal_weights(n1)
    w2 = v2.layer_equal_weights(n2)
    w3 = v2.layer_equal_weights(n3)
    s1, _ = v2.level_signal(n1, w1, data.get("nagr_nodes", []))
    s2, _ = v2.level_signal(n2, w2, data.get("nagr_nodes", []))
    s3, _ = v2.level_signal(n3, w3, data.get("nagr_nodes", []))
    regime, alphas = v2.router_weights(vol_pctl)
    overall = v2.combine_levels(s1, s2, s3, alphas)
    coverage = sum(len(x) > 0 for x in [n1, n2, n3]) / 3.0
    conf = round(0.5 + 0.5 * min(coverage, 1.0), 3)
    notes = []
    asof = fixed_ts or dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    out = {
        "asof": asof,
        "summary": {
            "scenario": scenario,
            "window": window,
            "overall_signal": round(overall, 6),
            "confidence": conf,
            "router_path": f"{scenario}/v2.fractal",
            "nagr_score": 0.0,
            "advisories": notes,
            "overall_signal_L1": round(s1, 6),
            "overall_signal_L2": round(s2, 6),
            "overall_signal_L3": round(s3, 6),
            "level_weights": alphas,
        },
        "details": {
            "normalized_micro": {k: round(v, 6) for k, v in n1.items()},
            "normalized_mezo": {k: round(v, 6) for k, v in n2.items()},
            "normalized_macro": {k: round(v, 6) for k, v in n3.items()},
            "router_regime": regime,
            "diagnostics": {"completeness": round(coverage, 3), "notes": notes},
        },
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


register_engine("v1", _run_v1)
register_engine("v2.fractal", _run_v2)

