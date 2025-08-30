#!/usr/bin/env python3
import sys
from pathlib import Path
import pytest

# Allow tests to import the project modules directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from btcmi.engine_v2 import (
    normalize_layer,
    linear_score,
    level_signal,
    router_weights,
    combine_levels,
)


def test_normalize_layer_handles_empty_and_non_numeric_and_extreme():
    assert normalize_layer({}, {"a": 1.0}) == {}
    feats = {"x": 1e6, "y": "bad"}
    scales = {"x": 1.0}
    norm = normalize_layer(feats, scales)
    assert set(norm.keys()) == {"x"}
    assert norm["x"] == pytest.approx(1.0)


def test_linear_score_zero_weights_and_missing_features():
    norm = {"a": 0.5}
    weights = {"a": 0.0, "b": 1.0}
    score, contrib = linear_score(norm, weights)
    assert score == 0.0
    assert contrib == {"a": 0.0}


def test_linear_score_clips_extreme_values():
    norm = {"a": 5.0}
    weights = {"a": 1.0}
    score, contrib = linear_score(norm, weights)
    assert score == 1.0
    assert contrib["a"] == 5.0


def test_level_signal_empty_inputs():
    sig, contrib = level_signal({}, {}, [])
    assert sig == 0.0
    assert contrib == {}


def test_level_signal_zero_weights_uses_nagr():
    norm = {"a": 1.0}
    weights = {"a": 0.0}
    nodes = [{"weight": 1.0, "score": 1.0}]
    sig, contrib = level_signal(norm, weights, nodes)
    assert sig == pytest.approx(0.2)
    assert contrib == {"a": 0.0}


def test_level_signal_extreme_inputs_clipped():
    norm = {"a": 5.0}
    weights = {"a": 1.0}
    nodes = [{"weight": 1.0, "score": 2.0}]
    sig, _ = level_signal(norm, weights, nodes)
    assert sig == 1.0


@pytest.mark.parametrize(
    "vol_pctl, expected",
    [
        (0.0, "low"),
        (0.2, "mid"),
        (0.6, "high"),
        (1.0, "high"),
    ],
)
def test_router_weights_boundaries(vol_pctl, expected):
    regime, w = router_weights(vol_pctl)
    assert regime == expected
    assert abs(sum(w.values()) - 1.0) < 1e-9


def test_combine_levels_zero_weights():
    sig = combine_levels(1.0, -1.0, 0.5, {"L1": 0.0, "L2": 0.0, "L3": 0.0})
    assert sig == 0.0


def test_combine_levels_extreme_values_clipped():
    sig = combine_levels(10.0, -10.0, 10.0, {"L1": 0.3, "L2": 0.3, "L3": 0.4})
    assert sig == 1.0
    sig_neg = combine_levels(-10.0, -10.0, -10.0, {"L1": 0.3, "L2": 0.3, "L3": 0.4})
    assert sig_neg == -1.0
