# Golden Files

This directory contains JSON "golden" files used by regression tests for the
API and engine runners.

## Regenerating

To update the engine outputs:

```
python -m cli.btcmi run --input btcmi/examples/intraday.json --mode v1 \
    --fixed-ts 2025-01-01T00:00:00Z --out tests/golden/intraday_v1.golden.json
python -m cli.btcmi run --input btcmi/examples/intraday_fractal.json --mode v2.fractal \
    --fixed-ts 2025-01-01T00:00:00Z --out tests/golden/intraday_fractal.golden.json
python -m cli.btcmi run --input btcmi/examples/swing_fractal.json --mode v2.fractal \
    --fixed-ts 2025-01-01T00:00:00Z --out tests/golden/swing_fractal.golden.json
```

API response snapshots are regenerated with:

```
UPDATE_SNAPSHOTS=1 pytest tests/test_api_snapshots.py
```

After regenerating, update checksums:

```
(cd tests/golden && sha256sum *.golden.json > CHECKSUMS.SHA256)
```
