import math
from hypothesis import given, strategies as st
from btcmi.engine_v1 import (
    normalize,
    base_signal,
    nagr_score,
    combine,
    SCENARIO_WEIGHTS,
    NORM_SCALE,
)

# Strategy for feature dictionaries
feature_names = list(NORM_SCALE.keys())


@given(
    st.dictionaries(
        st.sampled_from(feature_names),
        st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
        min_size=1,
    )
)
def test_normalize_bounds(features):
    norm = normalize(features)
    assert norm
    assert all(-1.0 <= v <= 1.0 for v in norm.values())


@given(
    st.sampled_from(list(SCENARIO_WEIGHTS.keys())),
    st.dictionaries(
        st.sampled_from(feature_names),
        st.floats(-1, 1, allow_nan=False, allow_infinity=False),
        min_size=1,
    ),
)
def test_base_signal_weights_and_bounds(scenario, norm):
    score, weights, _ = base_signal(scenario, norm)
    assert -1.0 <= score <= 1.0
    assert math.isclose(sum(abs(w) for w in weights.values()), 1.0)


@given(
    st.floats(-10, 10, allow_nan=False, allow_infinity=False),
    st.floats(-10, 10, allow_nan=False, allow_infinity=False),
)
def test_combine_clips(base, nagr):
    val = combine(base, nagr)
    assert -1.0 <= val <= 1.0


@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "weight": st.floats(-10, 10, allow_nan=False, allow_infinity=False),
                "score": st.floats(-10, 10, allow_nan=False, allow_infinity=False),
            }
        ),
        max_size=10,
    )
)
def test_nagr_score_bounds(nodes):
    val = nagr_score(nodes)
    assert -1.0 <= val <= 1.0
