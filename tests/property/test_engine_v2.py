import math
from hypothesis import given, strategies as st
from btcmi.engine_v2 import (
    tanh_norm,
    normalize_layer,
    router_weights,
    combine_levels,
    layer_equal_weights,
    level_signal,
    nagr,
    SCALES,
)

layers = list(SCALES.keys())


@st.composite
def layer_and_features(draw):
    layer = draw(st.sampled_from(layers))
    feats = draw(
        st.dictionaries(
            st.sampled_from(list(SCALES[layer].keys())),
            st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
            min_size=1,
        )
    )
    return layer, feats


@given(
    st.floats(-1e6, 1e6, allow_nan=False, allow_infinity=False),
    st.floats(0.1, 1e6, allow_nan=False, allow_infinity=False),
)
def test_tanh_norm_bounds(x, s):
    val = tanh_norm(x, s)
    assert -1.0 <= val <= 1.0


@given(layer_and_features())
def test_normalize_layer_bounds(data):
    layer, feats = data
    norm = normalize_layer(feats, SCALES[layer])
    assert norm
    assert all(-1.0 <= v <= 1.0 for v in norm.values())


@given(
    st.dictionaries(
        st.text(min_size=1),
        st.floats(-1, 1, allow_nan=False, allow_infinity=False),
        min_size=1,
    )
)
def test_layer_equal_weights_sum(norm):
    weights = layer_equal_weights(norm)
    assert weights
    assert math.isclose(sum(weights.values()), 1.0)


@given(st.floats(0, 1, allow_nan=False, allow_infinity=False))
def test_router_weights_sum(vol):
    _, weights = router_weights(vol)
    assert math.isclose(sum(weights.values()), 1.0)


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
def test_nagr_bounds(nodes):
    val = nagr(nodes)
    assert -1.0 <= val <= 1.0


@given(
    st.floats(0, 1, allow_nan=False, allow_infinity=False),
    st.floats(-10, 10, allow_nan=False, allow_infinity=False),
    st.floats(-10, 10, allow_nan=False, allow_infinity=False),
    st.floats(-10, 10, allow_nan=False, allow_infinity=False),
)
def test_combine_levels_clips(vol, L1, L2, L3):
    _, weights = router_weights(vol)
    assert math.isclose(sum(weights.values()), 1.0)
    score = combine_levels(L1, L2, L3, weights)
    assert -1.0 <= score <= 1.0


@st.composite
def level_input(draw):
    layer, feats = draw(layer_and_features())
    norm = normalize_layer(feats, SCALES[layer])
    weights = layer_equal_weights(norm)
    nodes = draw(
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
    return norm, weights, nodes


@given(level_input())
def test_level_signal_bounds(data):
    norm, weights, nodes = data
    score, _ = level_signal(norm, weights, nodes)
    assert -1.0 <= score <= 1.0
    if weights:
        assert math.isclose(sum(weights.values()), 1.0)
