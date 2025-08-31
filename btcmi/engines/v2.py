from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, Any

from btcmi.engine_v2 import (
    SCALES,
    normalize_layer,
    layer_equal_weights,
    level_signal,
    router_weights,
    combine_levels,
)
import btcmi.io
from .base import Engine


class EngineV2(Engine):
    """Second generation fractal engine."""

    def run(self, data: Dict[str, Any], fixed_ts, out_path: str | Path | None = None):
        scenario, window = self._validate_scenario_window(data)
        f1 = data.get("features_micro", {})
        f2 = data.get("features_mezo", {})
        f3 = data.get("features_macro", {})
        try:
            vol_pctl = float(data.get("vol_regime_pctl", 0.5))
        except (TypeError, ValueError) as exc:
            raise ValueError("'vol_regime_pctl' must be a number in [0, 1]") from exc
        if not 0.0 <= vol_pctl <= 1.0:
            raise ValueError("'vol_regime_pctl' must be a number in [0, 1]")
        n1 = normalize_layer(f1, SCALES["L1"])
        n2 = normalize_layer(f2, SCALES["L2"])
        n3 = normalize_layer(f3, SCALES["L3"])
        w1 = layer_equal_weights(n1)
        w2 = layer_equal_weights(n2)
        w3 = layer_equal_weights(n3)
        s1, _ = level_signal(n1, w1, data.get("nagr_nodes", []))
        s2, _ = level_signal(n2, w2, data.get("nagr_nodes", []))
        s3, _ = level_signal(n3, w3, data.get("nagr_nodes", []))
        regime, alphas = router_weights(vol_pctl)
        overall = combine_levels(s1, s2, s3, alphas)
        coverage = sum(len(x) > 0 for x in [n1, n2, n3]) / 3.0
        conf = round(0.5 + 0.5 * min(coverage, 1.0), 3)
        notes: list[str] = []
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
                "router_path": f"{scenario.value}/v2.fractal",
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
        if out_path is not None:
            btcmi.io.write_output(out, out_path)
        return out


__all__ = ["EngineV2"]
