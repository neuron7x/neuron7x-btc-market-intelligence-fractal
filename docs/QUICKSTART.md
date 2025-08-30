# Quickstart
## v1 (baseline)
btcmi run --input examples/intraday.json --out outputs/intraday_v1.out.json --mode v1 --fixed-ts 2025-01-01T00:00:00Z
## v2 Fractal
btcmi run --input examples/intraday_fractal.json --out outputs/intraday_v2.out.json --mode v2.fractal --fixed-ts 2025-01-01T00:00:00Z
## End-to-end evaluation
python examples/run_e2e.py

The script loads `examples/real_*.json`, runs the CLI, and reports metrics:
* per-example absolute error between predicted and reference signals;
* overall mean absolute error (MAE);
* Pearson correlation across all examples.

Lower MAE and higher correlation imply better agreement with the reference signals.
