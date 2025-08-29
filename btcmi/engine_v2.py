from __future__ import annotations
from typing import Dict, List, Tuple
import math


def is_number(x): return isinstance(x,(int,float))


def tanh_norm(x: float, s: float) -> float:
    return math.tanh(x/s) if s else 0.0


def normalize_layer(feats: Dict[str, float], scales: Dict[str, float]) -> Dict[str, float]:
    return {k: tanh_norm(v, scales.get(k,1.0)) for k,v in feats.items() if isinstance(v,(int,float))}


def linear_score(norm: Dict[str, float], weights: Dict[str, float]):
    s=0.0; den=0.0; contrib={}
    for k,w in weights.items():
        if k in norm:
            c=norm[k]*w; contrib[k]=c; s+=c; den+=abs(w)
    score = max(-1.0, min(1.0, s/den)) if den else 0.0
    return score, contrib


def nagr(nodes: List[dict]) -> float:
    if not nodes: return 0.0
    nodes=[n for n in nodes if is_number(n.get("weight")) and is_number(n.get("score"))]
    if not nodes: return 0.0
    num=sum(float(n.get("weight"))*float(n.get("score")) for n in nodes)
    den=sum(abs(float(n.get("weight"))) for n in nodes) or 1.0
    return max(-1.0, min(1.0, num/den))


def level_signal(norm, weights, nagr_nodes):
    base, contrib = linear_score(norm, weights)
    return 0.8*base + 0.2*nagr(nagr_nodes), contrib


def router_weights(vol_pctl: float):
    if vol_pctl < 0.2:   return "low", {"L1":0.15, "L2":0.35, "L3":0.50}
    if vol_pctl < 0.6:   return "mid", {"L1":0.25, "L2":0.40, "L3":0.35}
    return "high", {"L1":0.40, "L2":0.40, "L3":0.20}


def combine_levels(L1: float, L2: float, L3: float, w):
    s = w["L1"]*L1 + w["L2"]*L2 + w["L3"]*L3
    return max(-1.0, min(1.0, s))


SCALES = {
  "L1": {"price_change_pct":2.0,"volume_change_pct":50.0,"funding_rate_bps":10.0,"oi_change_pct":20.0,"micro_liquidity_gaps":5.0},
  "L2": {"oi_term_structure_slope":0.5,"funding_premium_spread":0.5,"net_positioning_index":0.5,"liquidation_heatmap_entropy":1.0},
  "L3": {"hashrate_trend":0.5,"active_addrs_trend":0.5,"supply_in_profit_pct":0.5,"macro_regime_score":1.0}
}


def layer_equal_weights(norm: Dict[str,float]) -> Dict[str,float]:
    if not norm: return {}
    n = len(norm); w = 1.0/n
    return {k: w for k in norm.keys()}
