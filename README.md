# BTC Market Intelligence — FRACTAL

Production-grade toolkit for Bitcoin market intelligence: strict data contracts, deterministic pipelines, validation, observability, and release artifacts.

## Features

* **Operational modes:** `quick_brief`, `pro_report`, `signal_scan`, `execution_plan`, `stress_test`, `backtest_hint`
* **Data contracts:** `input_schema.json`, `output_schema.json`
* **Validation & integrity:** structural validator, checksums, SBOM/provenance
* **Observability:** Prometheus job, Grafana dashboard
* **HTTP API:** `/run`, `/validate/{schema}`, `/metrics`, `/healthz` ([docs/API.md](docs/API.md))
* **Containerized runtime:** Docker Compose
* **Versioning:** semantic tags, `VERSION`, `CHANGELOG.md`
* **Conventional Commits** for history hygiene

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
pip install -r requirements.txt
pip install -e .
```

Run:

```bash
# Option 1: use module path directly
python -m cli.btcmi run --mode execution_plan --input examples/input.sample.json --out out.json
# Option 2: after installation, invoke the script
btcmi run --mode execution_plan --input examples/input.sample.json --out out.json
python tests/validate_output.py out.json  # validate against output_schema.json
```

### Platform notes

Scientific libraries such as `numpy` and `scipy` may require native build
tools.

* **Debian/Ubuntu:** `sudo apt install build-essential libopenblas-dev gfortran`
* **Windows:** install the Microsoft C++ Build Tools or use precompiled wheels

## Docker

```bash
docker compose up --build
docker compose run --rm app --mode quick_brief --input /data/input.json --out /data/out.json
```

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

## Releases

1. Tag `vX.Y.Z`
2. Create GitHub Release with `CHANGELOG.md` excerpt
3. Attach distributable ZIP as artifact

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
