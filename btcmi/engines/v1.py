from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, Any

from btcmi.engine_v1 import (
    normalize,
    base_signal,
    nagr_score,
    combine,
    completeness,
)
import btcmi.io
from .base import Engine


class EngineV1(Engine):
    """First generation signal engine."""

    def run(self, data: Dict[str, Any], fixed_ts, out_path: str | Path | None = None):
        scenario, window = self._validate_scenario_window(data)
        feats: Dict[str, float] = data.get("features", {})
        norm = normalize(feats)
        base_res = base_signal(scenario.value, norm)
        ng = nagr_score(data.get("nagr_nodes", []))
        overall = combine(base_res.score, ng)
        comp = completeness(feats)
        conf = round(0.5 + 0.5 * comp, 3)
        notes: list[str] = []
        constraints = False
        if comp < 0.6:
            notes.append("low_feature_completeness")
        asof = fixed_ts or dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        out = {
            "schema_version": data.get("schema_version", "2.0.0"),
            "lineage": data.get("lineage", {}),
            "asof": asof,
            "summary": {
                "scenario": scenario.value,
                "window": window.value,
                "overall_signal": round(overall, 6),
                "confidence": conf,
                "router_path": f"{scenario.value}/v1",
                "nagr_score": round(ng, 6),
                "advisories": notes,
            },
            "details": {
                "normalized_features": {k: round(v, 6) for k, v in norm.items()},
                "weights": base_res.weights,
                "contributions": {
                    k: round(v, 6) for k, v in base_res.contributions.items()
                },
                "constraints_applied": constraints,
                "diagnostics": {"completeness": round(comp, 3), "notes": notes},
            },
        }
        if out_path is not None:
            btcmi.io.write_output(out, out_path)
        return out


__all__ = ["EngineV1"]
