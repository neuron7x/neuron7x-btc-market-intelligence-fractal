"""Second generation layered signal engine utilities."""

from __future__ import annotations
from typing import Dict, List
import math
from btcmi.utils import is_number
from btcmi.config import SCALES as CONFIG_SCALES

SCALES = CONFIG_SCALES


def tanh_norm(x: float, s: float) -> float:
    """Normalize a value using hyperbolic tangent scaling.

    Args:
        x: Input value.
        s: Scale factor determining steepness.

    Returns:
        The normalized value in [-1, 1].

    """
    return math.tanh(x / s) if s else 0.0


def normalize_layer(
    feats: Dict[str, float], scales: Dict[str, float]
) -> Dict[str, float]:
    """Apply normalization to a layer's feature set.

    Args:
        feats: Raw feature values for the layer.
        scales: Scaling factors keyed by feature name.

    Returns:
        Dictionary of normalized feature values.

    """
    return {
        k: tanh_norm(v, scales.get(k, 1.0)) for k, v in feats.items() if is_number(v)
    }


def linear_score(norm: Dict[str, float], weights: Dict[str, float]):
    """Compute weighted linear score for normalized features.

    Args:
        norm: Normalized feature values.
        weights: Weight assigned to each feature.

    Returns:
        Tuple of overall score and per-feature contributions.

    """
    s = 0.0
    den = 0.0
    contrib = {}
    for k, w in weights.items():
        if k in norm:
            c = norm[k] * w
            contrib[k] = c
            s += c
            den += abs(w)
    score = max(-1.0, min(1.0, s / den)) if den else 0.0
    return score, contrib


def nagr(nodes: List[dict]) -> float:
    """Aggregate network graph ratings.

    Args:
        nodes: Sequence of node dicts with ``weight`` and ``score``.

    Returns:
        Weighted average score clipped to [-1, 1].

    """
    if not nodes:
        return 0.0
    num = sum(float(n.get("weight", 0.0)) * float(n.get("score", 0.0)) for n in nodes)
    den = sum(abs(float(n.get("weight", 0.0))) for n in nodes) or 1.0
    return max(-1.0, min(1.0, num / den))


def level_signal(norm, weights, nagr_nodes):
    """Blend linear feature score with network rating for one level.

    Args:
        norm: Normalized feature values.
        weights: Weight mapping for the level.
        nagr_nodes: Network graph nodes contributing to NAGR score.

    Returns:
        Tuple of combined level signal and feature contributions.

    """
    base, contrib = linear_score(norm, weights)
    return 0.8 * base + 0.2 * nagr(nagr_nodes), contrib


def router_weights(vol_pctl: float):
    """Select level weights based on volume percentile.

    Args:
        vol_pctl: Market volume percentile in [0, 1].

    Returns:
        A tuple of descriptor string and weight mapping for levels.

    """
    if vol_pctl < 0.2:
        return "low", {"L1": 0.15, "L2": 0.35, "L3": 0.50}
    if vol_pctl < 0.6:
        return "mid", {"L1": 0.25, "L2": 0.40, "L3": 0.35}
    return "high", {"L1": 0.40, "L2": 0.40, "L3": 0.20}


def combine_levels(L1: float, L2: float, L3: float, w):
    """Merge signals from all levels using provided weights.

    Args:
        L1: Level-one signal value.
        L2: Level-two signal value.
        L3: Level-three signal value.
        w: Weight mapping for each level.

    Returns:
        Combined score clipped to [-1, 1].

    """
    s = w["L1"] * L1 + w["L2"] * L2 + w["L3"] * L3
    return max(-1.0, min(1.0, s))




def layer_equal_weights(norm: Dict[str, float]) -> Dict[str, float]:
    """Generate equal weights for a layer's features.

    Args:
        norm: Normalized feature values for a layer.

    Returns:
        Mapping assigning an equal weight to each feature.

    """
    if not norm:
        return {}
    n = len(norm)
    w = 1.0 / n
    return {k: w for k in norm.keys()}
