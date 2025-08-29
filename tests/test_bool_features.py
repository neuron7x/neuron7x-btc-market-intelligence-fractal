import sys
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
from btcmi import engine_v1 as v1
from btcmi import engine_v2 as v2

def test_engine_v1_normalize_ignores_bool():
    feats = {"price_change_pct": 0.5, "volume_change_pct": True, "oi_change_pct": 0.1}
    norm = v1.normalize(feats)
    assert "volume_change_pct" not in norm
    expected = v1.normalize({"price_change_pct": 0.5, "oi_change_pct": 0.1})
    assert norm == expected
    base1, _, _ = v1.base_signal("intraday", norm)
    base2, _, _ = v1.base_signal("intraday", expected)
    assert base1 == base2
    comp1 = v1.completeness(norm)
    comp2 = v1.completeness(expected)
    assert comp1 == comp2

def test_engine_v2_normalize_layer_ignores_bool():
    feats = {"price_change_pct": 0.5, "volume_change_pct": False}
    norm = v2.normalize_layer(feats, v2.SCALES["L1"])
    assert "volume_change_pct" not in norm
    expected = v2.normalize_layer({"price_change_pct": 0.5}, v2.SCALES["L1"])
    assert norm == expected

def test_nagr_functions_ignore_bool_nodes():
    nodes = [
        {"weight": 1, "score": 0.5},
        {"weight": True, "score": 0.9},
        {"weight": 0.5, "score": False},
        {"weight": 2, "score": 0.25},
    ]
    expected_v1 = v1.nagr_score([nodes[0], nodes[3]])
    assert v1.nagr_score(nodes) == expected_v1
    expected_v2 = v2.nagr([nodes[0], nodes[3]])
    assert v2.nagr(nodes) == expected_v2
