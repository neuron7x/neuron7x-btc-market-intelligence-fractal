"""NF3P prediction and backtest utilities."""
from __future__ import annotations

from typing import Dict, Tuple

from btcmi.engine_v2 import SCALES, normalize_layer, layer_equal_weights
from btcmi.feature_processing import weighted_score


def predictions_and_backtest(
    f1: Dict[str, float],
    f2: Dict[str, float],
    f3: Dict[str, float],
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Return per-level predictions and simple backtest metrics.

    Parameters
    ----------
    f1, f2, f3:
        Feature mappings for micro, mezo and macro layers respectively.

    Returns
    -------
    Tuple[Dict[str, float], Dict[str, float]]
        A tuple containing the predictions for each layer and basic
        backtest metrics computed from those predictions.
    """
    n1 = normalize_layer(f1, SCALES["L1"])
    n2 = normalize_layer(f2, SCALES["L2"])
    n3 = normalize_layer(f3, SCALES["L3"])

    w1 = layer_equal_weights(n1)
    w2 = layer_equal_weights(n2)
    w3 = layer_equal_weights(n3)

    p1, _ = weighted_score(n1, w1)
    p2, _ = weighted_score(n2, w2)
    p3, _ = weighted_score(n3, w3)

    predictions = {
        "L1": round(p1, 6),
        "L2": round(p2, 6),
        "L3": round(p3, 6),
    }

    mse = sum(v * v for v in predictions.values()) / 3.0
    mae = sum(abs(v) for v in predictions.values()) / 3.0
    backtest = {"mse": round(mse, 6), "mae": round(mae, 6)}
    return predictions, backtest


__all__ = ["predictions_and_backtest"]
