"""Shared configuration constants for the BTC Market Intelligence engines."""

SCENARIO_WEIGHTS = {
    "intraday": {
        "price_change_pct": 0.35,
        "volume_change_pct": 0.25,
        "funding_rate_bps": -0.10,
        "oi_change_pct": 0.20,
        "onchain_active_addrs_change_pct": 0.10,
    },
    "scalp": {
        "price_change_pct": 0.45,
        "volume_change_pct": 0.30,
        "funding_rate_bps": -0.05,
        "oi_change_pct": 0.15,
        "onchain_active_addrs_change_pct": 0.05,
    },
    "swing": {
        "price_change_pct": 0.25,
        "volume_change_pct": 0.15,
        "funding_rate_bps": -0.10,
        "oi_change_pct": 0.25,
        "onchain_active_addrs_change_pct": 0.25,
    },
}

NORM_SCALE = {
    "price_change_pct": 2.0,
    "volume_change_pct": 50.0,
    "funding_rate_bps": 10.0,
    "oi_change_pct": 20.0,
    "onchain_active_addrs_change_pct": 20.0,
}

SCALES = {
    "L1": {
        "price_change_pct": 2.0,
        "volume_change_pct": 50.0,
        "funding_rate_bps": 10.0,
        "oi_change_pct": 20.0,
        "micro_liquidity_gaps": 5.0,
    },
    "L2": {
        "oi_term_structure_slope": 0.5,
        "funding_premium_spread": 0.5,
        "net_positioning_index": 0.5,
        "liquidation_heatmap_entropy": 1.0,
    },
    "L3": {
        "hashrate_trend": 0.5,
        "active_addrs_trend": 0.5,
        "supply_in_profit_pct": 0.5,
        "macro_regime_score": 1.0,
    },
}

__all__ = ["SCENARIO_WEIGHTS", "NORM_SCALE", "SCALES"]
