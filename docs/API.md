# API Usage

## FastAPI server

Install dependencies:

```bash
pip install fastapi uvicorn
```

Run the server:

```bash
uvicorn btcmi.api:app --host 0.0.0.0 --port 8000
```

POST an input payload:

```bash
curl -X POST "http://localhost:8000/run?fractal=true&fixed_ts=2025-01-01T00:00:00Z" \
  -H "Content-Type: application/json" \
  -d @examples/intraday_fractal.json
```

## Docker

Build and run with Docker:

```bash
docker build -t btcmi-api -f docker/Dockerfile .
docker run --rm -p 8000:8000 btcmi-api \
  uvicorn btcmi.api:app --host 0.0.0.0 --port 8000
```

## Determinism and seeds

Use a fixed timestamp and Python hash seed for reproducible runs:

```bash
PYTHONHASHSEED=0 uvicorn btcmi.api:app --host 0.0.0.0 --port 8000
```

## Metrics

Expose basic metrics:

```bash
python ops/metrics/exporter.py
# metrics at http://localhost:9101/metrics
```

## Release artifacts

Published releases include checksums and an SBOM in `provenance/`. See `CHECKSUMS.SHA256` and `provenance/sbom.spdx.json` for verification.
