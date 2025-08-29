# Quickstart
## v1 (baseline)
python3 cli/btcmi.py run --input examples/intraday.json --out outputs/intraday_v1.out.json --fixed-ts 2025-01-01T00:00:00Z
see `examples/golden/intraday_v1.json`
## v2 Fractal
python3 cli/btcmi.py run --input examples/intraday_fractal.json --out outputs/intraday_v2.out.json --fractal --fixed-ts 2025-01-01T00:00:00Z
see `examples/golden/intraday_fractal.json` and `examples/golden/swing_fractal.json`
