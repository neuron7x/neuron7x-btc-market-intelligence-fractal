# Quickstart
Use `--seed` with `--deterministic` for reproducible runs.
## v1 (baseline)
python3 cli/btcmi.py run --input examples/intraday.json --out outputs/intraday_v1.out.json --fixed-ts 2025-01-01T00:00:00Z --seed 1 --deterministic
## v2 Fractal
python3 cli/btcmi.py run --input examples/intraday_fractal.json --out outputs/intraday_v2.out.json --fractal --fixed-ts 2025-01-01T00:00:00Z --seed 1 --deterministic
