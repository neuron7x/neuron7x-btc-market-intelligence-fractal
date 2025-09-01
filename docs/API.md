# HTTP API

This service exposes a minimal FastAPI interface for running analyses, validating JSON payloads and reporting status.

The OpenAPI schema is available in [openapi.json](openapi.json).

Available endpoints:

- `POST /run` – execute an analysis run.
- `POST /validate/{schema}` – validate payloads against `input` or `output` schemas.
- `GET /metrics` – expose Prometheus metrics.
- `GET /healthz` – health check for liveness monitoring.

All POST endpoints require an API key via the `X-API-Key` header. Configure the
expected token with the `BTCMI_API_KEY` environment variable (default
`changeme`).

## Running the server

After installing `btcmi`, launch the API with:

```bash
uvicorn btcmi.api:app
```

## Authentication

All secured endpoints expect an API key in the `X-API-Key` header. Set the
expected value through the `BTCMI_API_KEY` environment variable (defaults to
`changeme`).

## `POST /run`

Execute an analysis run. The payload must conform to `input_schema.json` and specify the desired mode (`v1` or `v2.fractal`).

The heavy computation is executed in a background thread so the API
remains responsive and other requests are not blocked while the run is
in progress.

### Example

**Request**

```json
{
  "schema_version": "2.0.0",
  "lineage": {"run_id": "00000000000000000000000000000000"},
  "scenario": "intraday",
  "window": "1h",
  "mode": "v1",
  "features": {"btc_price": 30000}
}
```

```bash
curl -X POST http://localhost:8000/run \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: changeme' \
  -d @examples/intraday.json
```

**Response**

```json
{
  "meta": {"mode": "v1", "ts": "2025-01-01T00:00:00Z"},
  "dashboard": {"summary": "..."}
}
```

**Error codes**

| code | reason                          |
|------|---------------------------------|
| 401  | invalid or missing API key      |
| 400  | unknown mode or validation fail |
| 500  | internal error                  |

## `POST /validate/{schema}`

Validate a payload against a registered schema (`input` or `output`).

### Example

**Request**

```json
{
  "schema_version": "2.0.0",
  "lineage": {"run_id": "00000000000000000000000000000000"},
  "scenario": "intraday",
  "window": "1h",
  "mode": "v1",
  "features": {"btc_price": 30000}
}
```

```bash
curl -X POST http://localhost:8000/validate/input \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: changeme' \
  -d @examples/intraday.json
```

**Response**

```json
{"valid": true}
```

**Error codes**

| code | reason                |
|------|-----------------------|
| 401  | invalid or missing API key |
| 400  | validation failed     |
| 404  | schema not found      |

## `GET /metrics`

Prometheus metrics endpoint.

### Example

**Request**

```bash
curl http://localhost:8000/metrics
```

**Response**

```
btcmi_requests{endpoint="/run"} 1
```

**Error codes**

| code | reason             |
|------|--------------------|
| 500  | internal error     |

## `GET /healthz`

Simple health check.

### Example

**Request**

```bash
curl http://localhost:8000/healthz
```

**Response**

```json
{"status": "ok"}
```

**Error codes**

| code | reason         |
|------|----------------|
| 500  | internal error |

