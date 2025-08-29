"""First generation signal calculation utilities."""

from __future__ import annotations
from typing import Dict, Any
import math
from btcmi.utils import is_number


FeatureMap = Dict[str, float]
SCENARIO_WEIGHTS = {
    "intraday": {"price_change_pct":0.35,"volume_change_pct":0.25,"funding_rate_bps":-0.10,"oi_change_pct":0.20,"onchain_active_addrs_change_pct":0.10},
    "scalp":    {"price_change_pct":0.45,"volume_change_pct":0.30,"funding_rate_bps":-0.05,"oi_change_pct":0.15,"onchain_active_addrs_change_pct":0.05},
    "swing":    {"price_change_pct":0.25,"volume_change_pct":0.15,"funding_rate_bps":-0.10,"oi_change_pct":0.25,"onchain_active_addrs_change_pct":0.25},
}
NORM_SCALE = {"price_change_pct":2.0,"volume_change_pct":50.0,"funding_rate_bps":10.0,"oi_change_pct":20.0,"onchain_active_addrs_change_pct":20.0}
def normalize(features: FeatureMap) -> FeatureMap:
    """Scale raw feature values using hyperbolic tangent.

    Args:
        features: Mapping from feature names to raw numeric values.

    Returns:
        A feature map with each numeric value normalized to the [-1, 1] range.

    """
    return {k: math.tanh(v / NORM_SCALE.get(k, 1.0)) for k, v in features.items() if is_number(v)}


def completeness(features: FeatureMap) -> float:
    """Compute fraction of expected features present with numeric values.

    Args:
        features: Mapping of provided features.

    Returns:
        The proportion of expected features that are present and numeric.

    """
    exp = set(NORM_SCALE.keys())
    pres = {k for k, v in features.items() if k in exp and is_number(v)}
    return len(pres) / len(exp) if exp else 1.0
def base_signal(scenario: str, norm: FeatureMap):
    """Calculate weighted signal for a trading scenario.

    Args:
        scenario: Scenario key selecting the weight profile.
        norm: Normalized feature values.

    Returns:
        Tuple of overall score, applied weights, and individual contributions.

    """
    weights = SCENARIO_WEIGHTS[scenario]; s = 0.0; den = 0.0; contrib = {}
    for k, w in weights.items():
        if k in norm:
            c = norm[k] * w; contrib[k] = c; s += c; den += abs(w)
    return (max(-1.0, min(1.0, s / den)) if den else 0.0, weights, contrib)
def nagr_score(nodes: Any) -> float:
    """Aggregate a network graph rating score.

    Args:
        nodes: Iterable of node dictionaries with ``weight`` and ``score``.

    Returns:
        Weighted average score clipped to [-1, 1].

    """
    if not nodes:
        return 0.0
    num = 0.0; den = 0.0
    for n in nodes:
        w = float(n.get("weight", 0.0)); sc = float(n.get("score", 0.0)); num += w * sc; den += abs(w)
    return max(-1.0, min(1.0, num / den if den else 0.0))
def combine(base: float, nagr: float) -> float:
    """Blend base and network scores.

    Args:
        base: Baseline signal score.
        nagr: Network aggregated score.

    Returns:
        Weighted combination clipped to [-1, 1].

    """
    return max(-1.0, min(1.0, 0.7 * base + 0.3 * nagr))
