import pytest

pytest.importorskip("hypothesis")
from hypothesis import given, strategies as st

from btcmi.engine_v1 import nagr_score, combine
from btcmi.config import NORM_SCALE
from btcmi.feature_processing import normalize_features


@given(
    st.dictionaries(
        keys=st.text(min_size=1),
        values=st.floats(
            min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
        ),
    )
)
def test_normalize_outputs_clamped(features):
    norm = normalize_features(features, NORM_SCALE)
    assert all(-1.0 <= v <= 1.0 for v in norm.values())


@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "weight": st.floats(
                    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
                ),
                "score": st.floats(
                    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
                ),
            }
        )
    )
)
def test_nagr_score_clamped(nodes):
    result = nagr_score(nodes)
    assert -1.0 <= result <= 1.0


@given(
    st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
)
def test_combine_clamped(base, nagr):
    result = combine(base, nagr)
    assert -1.0 <= result <= 1.0
