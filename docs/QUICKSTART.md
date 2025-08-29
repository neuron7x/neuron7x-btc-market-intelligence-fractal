# Quickstart
## v1 (baseline)
python3 cli/btcmi.py run --input examples/intraday.json --out outputs/intraday_v1.out.json --fixed-ts 2025-01-01T00:00:00Z
## v2 Fractal
python3 cli/btcmi.py run --input examples/intraday_fractal.json --out outputs/intraday_v2.out.json --fractal --fixed-ts 2025-01-01T00:00:00Z

## Deterministic mode

Set a fixed timestamp and seed to make runs reproducible:

```bash
PYTHONHASHSEED=0 python3 cli/btcmi.py run --input examples/intraday.json \
  --out outputs/intraday_seeded.json --fixed-ts 2025-01-01T00:00:00Z
```

Metrics can be exposed separately:

```bash
python ops/metrics/exporter.py  # http://localhost:9101/metrics
```
