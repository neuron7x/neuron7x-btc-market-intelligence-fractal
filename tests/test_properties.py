import string

import pytest

from btcmi.engine_v1 import normalize
from btcmi.engine_v2 import normalize_layer, router_weights

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, strategies as st

key_strategy = st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=5)
value_strategy = st.one_of(
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=5),
)


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_router_weights_properties(vol):
    regime, weights = router_weights(vol)
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    if vol < 0.2:
        assert regime == "low"
    elif vol < 0.6:
        assert regime == "mid"
    else:
        assert regime == "high"
    regime2, weights2 = router_weights(vol)
    assert regime2 == regime
    assert weights2 == weights


@given(st.dictionaries(key_strategy, value_strategy, max_size=5))
def test_v1_normalize_properties(features):
    out = normalize(features)
    assert set(out.keys()) == {k for k, v in features.items() if isinstance(v, (int, float))}
    assert all(-1.0 <= v <= 1.0 for v in out.values())


@given(st.dictionaries(key_strategy, value_strategy, max_size=5))
def test_v2_normalize_layer_properties(features):
    scales = {k: 1.0 for k in features.keys()}
    out = normalize_layer(features, scales)
    assert set(out.keys()) == {k for k, v in features.items() if isinstance(v, (int, float))}
    assert all(-1.0 <= v <= 1.0 for v in out.values())


def test_normalize_layer_zero_scale():
    feats = {"a": 5.0}
    scales = {"a": 0.0}
    out = normalize_layer(feats, scales)
    assert out["a"] == 0.0


def test_normalize_empty():
    assert normalize({}) == {}
    assert normalize_layer({}, {}) == {}

