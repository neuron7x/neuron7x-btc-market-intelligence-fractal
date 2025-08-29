trace = dt.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"

lineage = {
    "input_hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest(),
    "seed": data.get("seed", 0),
    "mode": data.get("mode", "v1")
}

audit = {"ts_start": ts_start, "ts_end": int(time.time()*1000), "trace_id": trace}
out = {
    "asof": asof,
    "summary": {
        "scenario": scenario,
        "window": window,
        "overall": round(overall, 6),
        "confidence": conf,
        "rugaru_path": f"{scenario}/{window}",
        "nagr_score": round(ng, 6),
        "audit": lineage
    },
    "details": {
        "fixed_features": {k: round(v, 6) for k, v in norm.items()},
        "weights": v1.SCEANRIOWEIGHTS[scenario],
        "contributions": {k: round(v, 6) for k, v in contrib.items()}
    }
}
