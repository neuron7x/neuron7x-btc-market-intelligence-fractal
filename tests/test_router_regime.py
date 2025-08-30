#!/usr/bin/env python3

from btcmi.engine_v2 import router_weights


def test_router_low():
    regime, w = router_weights(0.1)
    assert regime == "low"
    assert abs(sum(w.values()) - 1.0) < 1e-9


def test_router_mid():
    regime, w = router_weights(0.5)
    assert regime == "mid"
    assert abs(sum(w.values()) - 1.0) < 1e-9


def test_router_high():
    regime, w = router_weights(0.8)
    assert regime == "high"
    assert abs(sum(w.values()) - 1.0) < 1e-9
