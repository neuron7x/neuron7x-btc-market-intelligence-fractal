"""Shared feature processing utilities."""

from __future__ import annotations

from typing import Dict, Tuple
import math

from btcmi.utils import is_number


FeatureMap = Dict[str, float]


def normalize_features(features: FeatureMap, scales: Dict[str, float]) -> FeatureMap:
    """Normalize raw feature values using hyperbolic tangent scaling.

    Args:
        features: Mapping from feature names to raw numeric values.
        scales: Per-feature scale factors controlling the steepness.

    Returns:
        A mapping of normalized feature values clipped to ``[-1, 1]``.
    """

    return {
        k: math.tanh(v / scales.get(k, 1.0))
        for k, v in features.items()
        if is_number(v)
    }


def weighted_score(norm: FeatureMap, weights: Dict[str, float]) -> Tuple[float, FeatureMap]:
    """Compute a weighted score from normalized features.

    Args:
        norm: Normalized feature values.
        weights: Weight assigned to each feature.

    Returns:
        Tuple of overall score and per-feature contributions.
    """

    s = 0.0
    den = 0.0
    contrib: FeatureMap = {}
    for k, w in weights.items():
        if k in norm:
            c = norm[k] * w
            contrib[k] = c
            s += c
            den += abs(w)
    score = max(-1.0, min(1.0, s / den)) if den else 0.0
    return score, contrib


__all__ = ["normalize_features", "weighted_score"]

