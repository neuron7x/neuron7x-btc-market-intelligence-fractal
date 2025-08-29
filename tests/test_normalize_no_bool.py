import math

from btcmi.engine_v1 import NORM_SCALE, normalize
from btcmi.engine_v2 import SCALES, normalize_layer


def test_v1_ignores_booleans():
    features = {"price_change_pct": 1.0, "volume_change_pct": True}
    result = normalize(features)
    assert "volume_change_pct" not in result
    assert result == {
        "price_change_pct": math.tanh(1.0 / NORM_SCALE["price_change_pct"])
    }


def test_v2_ignores_booleans():
    feats = {"price_change_pct": 1.0, "volume_change_pct": True}
    result = normalize_layer(feats, SCALES["L1"])
    assert "volume_change_pct" not in result
    assert result == {
        "price_change_pct": math.tanh(1.0 / SCALES["L1"]["price_change_pct"])
    }
