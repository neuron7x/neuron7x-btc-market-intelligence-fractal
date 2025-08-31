from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, Any

from btcmi.engine_nf3p import predictions_and_backtest
import btcmi.io
from .base import Engine


class EngineNF3P(Engine):
    """NF3P prediction engine."""

    def run(self, data: Dict[str, Any], fixed_ts, out_path: str | Path | None = None):
        scenario, window = self._validate_scenario_window(data)
        f1 = data.get("features_micro", {})
        f2 = data.get("features_mezo", {})
        f3 = data.get("features_macro", {})
        predictions, backtest = predictions_and_backtest(f1, f2, f3)
        asof = fixed_ts or dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        out = {
            "schema_version": data.get("schema_version", "2.0.0"),
            "lineage": data.get("lineage", {}),
            "asof": asof,
            "scenario": scenario.value,
            "window": window.value,
            "predictions": predictions,
            "backtest": backtest,
        }
        if out_path is not None:
            btcmi.io.write_output(out, out_path)
        return out


__all__ = ["EngineNF3P"]
