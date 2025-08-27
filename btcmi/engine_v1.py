from __future__ import annotations
from typing import Dict, Tuple, Any
import math
FeatureMap = Dict[str, float]
SCENARIO_WEIGHTS = {
    "intraday": {"price_change_pct":0.35,"volume_change_pct":0.25,"funding_rate_bps":-0.10,"oi_change_pct":0.20,"onchain_active_addrs_change_pct":0.10},
    "scalp":    {"price_change_pct":0.45,"volume_change_pct":0.30,"funding_rate_bps":-0.05,"oi_change_pct":0.15,"onchain_active_addrs_change_pct":0.05},
    "swing":    {"price_change_pct":0.25,"volume_change_pct":0.15,"funding_rate_bps":-0.10,"oi_change_pct":0.25,"onchain_active_addrs_change_pct":0.25},
}
NORM_SCALE = {"price_change_pct":2.0,"volume_change_pct":50.0,"funding_rate_bps":10.0,"oi_change_pct":20.0,"onchain_active_addrs_change_pct":20.0}
def normalize(features: FeatureMap) -> FeatureMap:
    return {k: math.tanh(v/NORM_SCALE.get(k,1.0)) for k,v in features.items() if isinstance(v,(int,float))}
def completeness(features: FeatureMap) -> float:
    exp=set(NORM_SCALE.keys()); pres=set(k for k in features.keys() if k in exp); 
    return len(pres)/len(exp) if exp else 1.0
def base_signal(scenario: str, norm: FeatureMap):
    weights=SCENARIO_WEIGHTS[scenario]; s=0.0; den=0.0; contrib={}
    for k,w in weights.items():
        if k in norm:
            c=norm[k]*w; contrib[k]=c; s+=c; den+=abs(w)
    return (max(-1.0,min(1.0,s/den)) if den else 0.0, weights, contrib)
def nagr_score(nodes: Any) -> float:
    if not nodes: return 0.0
    num=0.0; den=0.0
    for n in nodes: 
        w=float(n.get("weight",0.0)); sc=float(n.get("score",0.0)); num+=w*sc; den+=abs(w)
    return max(-1.0,min(1.0, num/den if den else 0.0))
def combine(base: float, nagr: float) -> float:
    return max(-1.0, min(1.0, 0.7*base + 0.3*nagr))
