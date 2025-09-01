# BTC Market Intelligence — FRACTAL

Production-grade toolkit for Bitcoin market intelligence: strict data contracts, deterministic pipelines, validation, observability, and release artifacts.

## Features

* **Operational modes:** `quick_brief`, `pro_report`, `signal_scan`, `execution_plan`, `stress_test`, `backtest_hint`
* **Data contracts:** `input_schema.json`, `output_schema.json`
* **Validation & integrity:** structural validator, checksums, SBOM/provenance
* **Observability:** Prometheus job, Grafana dashboard
* **HTTP API:** `/run`, `/validate/{schema}`, `/metrics`, `/healthz` (API key via `X-API-Key`; [docs/API.md](docs/API.md), [openapi.json](docs/openapi.json))
* **Containerized runtime:** Docker Compose
* **Versioning:** update the root `VERSION` file (single source of truth) and sync `CHANGELOG.md`
* **Conventional Commits** for history hygiene
* **Documentation:** [Architecture overview](docs/Architecture.md), [JSON field order](docs/FieldOrder.md)

## Repository layout

```
btcmi/               # core package
cli/                 # CLI entrypoints
docker/              # container images
docs/                # guides, SECURITY.md
examples/            # sample inputs/outputs
ops/                 # prometheus/, grafana/
provenance/          # sbom.spdx.json
scripts/             # generate_sbom.py, verify_checksums.py
tests/               # validators, fixtures
CHECKSUMS.SHA256
VERSION
CHANGELOG.md
docker-compose.yml
input_schema.json
output_schema.json
pyproject.toml
requirements.txt
```

## Quickstart (local)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt
pip install -e .
```

Run:

```bash
# Option 1: use module path directly
python -m cli.btcmi run --input examples/intraday.json --out out.json --mode v1
# Option 2: after installation, invoke the script
btcmi run --input examples/intraday.json --out out.json --mode v1
# Option 3: pipe data via stdin
cat examples/intraday.json | btcmi run --input - --mode v1
curl -s https://example.com/intraday.json | btcmi run --input - --mode v1
# Emit machine-readable errors as JSON
btcmi run --input bad.json --mode v1 --json-errors
# Enable Fractal Engine v2
btcmi run --input examples/intraday_fractal.json --out out_fractal.json --mode v2.fractal
python tests/validate_output.py out.json  # validate against output_schema.json
```

Start the HTTP API server:

```bash
export BTCMI_API_KEY=changeme  # set your preferred token
uvicorn btcmi.api:app
```

Requests to `/run` and `/validate/{schema}` must include `X-API-Key` in the
headers. Refer to [docs/API.md](docs/API.md) or the [OpenAPI schema](docs/openapi.json) for available endpoints and examples.

### Platform notes

Scientific libraries such as `numpy` and `scipy` may require native build
tools.

* **Debian/Ubuntu:** `sudo apt install build-essential libopenblas-dev gfortran`
* **Windows:** install the Microsoft C++ Build Tools or use precompiled wheels

## Docker

```bash
docker compose up --build
docker compose run --rm app --input /data/input.json --out /data/out.json
```

## Custom engines

Third-party packages can expose additional engines by registering a callable in
the engine registry:

```python
# mypkg/myengine.py
from btcmi.engines import register_engine

def run(self, data, fixed_ts, out_path=None):
    # ... perform custom processing ...
    return {"schema_version": "2.0.0", "summary": {"scenario": data["scenario"], "window": data["window"]}, "details": {}}

register_engine("my.mode", run)
```

Importing this module (or exposing it via the ``btcmi.engines`` entry point
group) makes ``my.mode`` available to ``load_runners()`` and the HTTP API.

## Modes

| mode            | purpose                                 | output                               |
| --------------- | --------------------------------------- | ------------------------------------ |
| quick\_brief    | short situational overview              | concise JSON/text                    |
| pro\_report     | full structured analysis                | JSON aligned to `output_schema.json` |
| signal\_scan    | signal sweep (spot/derivs/on-chain)     | signals block                        |
| execution\_plan | entries, triggers, invalidation, sizing | entries + risk                       |
| stress\_test    | adverse scenarios & sensitivities       | scenarios + risk notes               |
| backtest\_hint  | heuristic anchors for offline testing   | hints / parameter ranges             |

## Data contracts

* **Input:** timeframe, window, spot, derivatives, orderbook, onchain, macro, sentiment, constraints, preferences (`input_schema.json`).
* **Output:** meta, dashboard, scenarios, liquidity\_zones, derivatives, onchain, macro, entries, risk, qa, assurance (`output_schema.json`).

## Validation & integrity

This project relies on the [`jsonschema`](https://pypi.org/project/jsonschema/)
package for contract enforcement. Install it with `pip install jsonschema` if
it's not already available. Use the helper below to confirm a run complies with
`output_schema.json`.

```bash
sha256sum -c CHECKSUMS.SHA256
python scripts/verify_checksums.py
```

## Observability

* Prometheus job: `ops/prometheus/job.sample.yml`
* Grafana dashboard: `ops/grafana/dashboard.json`

Import the dashboard into Grafana:

1. Open Grafana and click the **+** icon in the sidebar.
2. Select **Import**.
3. Upload `ops/grafana/dashboard.json` or paste its JSON.
4. Choose your Prometheus data source and click **Import**.

## Releases

1. Update `VERSION` and `CHANGELOG.md`
2. Tag `vX.Y.Z`
3. Create GitHub Release with `CHANGELOG.md` excerpt
4. Attach distributable ZIP as artifact

## Contributing

* Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
* PRs must pass validators and keep schemas stable or bump versions accordingly.

## Security

Refer to `docs/SECURITY.md`. Report issues via GitHub Issues (Security).

## License

MIT. Educational use only. No financial advice. Timezone: Europe/Kyiv; ISO-8601 timestamps.
<!-- trigger security -->


## Maintainer

Yaroslav (**neuron7x**) — issues and maintenance via this repository.
