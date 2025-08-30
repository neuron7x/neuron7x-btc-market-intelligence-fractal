#!/usr/bin/env python3
import pytest

from btcmi.engine_v1 import normalize, completeness, base_signal, nagr_score, combine
from btcmi.config import NORM_SCALE, SCENARIO_WEIGHTS


@pytest.fixture
def raw_features():
    return {
        "price_change_pct": 1e6,
        "volume_change_pct": -1e6,
        "funding_rate_bps": "bad",
        "oi_change_pct": 1.0,
        "extra": 123,
    }


@pytest.fixture
def norm_extreme():
    return {k: 5.0 for k in NORM_SCALE.keys()}


def test_normalize_handles_non_numeric_and_extreme(raw_features):
    assert normalize({}) == {}
    norm = normalize(raw_features)
    assert set(norm.keys()) == {
        "price_change_pct",
        "volume_change_pct",
        "oi_change_pct",
        "extra",
    }
    assert norm["price_change_pct"] == pytest.approx(1.0)
    assert norm["volume_change_pct"] == pytest.approx(-1.0)


def test_completeness_counts_numeric_only(raw_features):
    assert completeness({}) == 0.0
    comp = completeness(raw_features)
    assert comp == pytest.approx(3 / len(NORM_SCALE))


def test_base_signal_empty_inputs():
    score, weights, contrib = base_signal("intraday", {})
    assert score == 0.0
    assert contrib == {}
    assert weights == SCENARIO_WEIGHTS["intraday"]


def test_base_signal_uses_present_features():
    score, _, contrib = base_signal("intraday", {"price_change_pct": 1.0})
    assert score == 1.0
    assert contrib == {"price_change_pct": pytest.approx(0.35)}


def test_base_signal_clips_extreme(norm_extreme):
    score, _, _ = base_signal("intraday", norm_extreme)
    assert score == 1.0
    neg = {k: -v for k, v in norm_extreme.items()}
    score_neg, _, _ = base_signal("intraday", neg)
    assert score_neg == -1.0


def test_nagr_score_handles_empty_and_zero_weights():
    assert nagr_score([]) == 0.0
    assert nagr_score([{"weight": 0.0, "score": 1.0}]) == 0.0


def test_nagr_score_clips_extreme():
    nodes = [{"weight": 1.0, "score": 2.0}]
    assert nagr_score(nodes) == 1.0


def test_combine_zero_scores():
    assert combine(0.0, 0.0) == 0.0


@pytest.mark.parametrize(
    "base, nagr, expected",
    [
        (10.0, 10.0, 1.0),
        (-10.0, -10.0, -1.0),
    ],
)
def test_combine_extreme_values_clipped(base, nagr, expected):
    assert combine(base, nagr) == expected
