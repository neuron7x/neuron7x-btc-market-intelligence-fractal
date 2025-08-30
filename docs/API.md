# HTTP API

This service exposes a minimal FastAPI interface for running analyses, validating JSON payloads and reporting status.

## Running the server

After installing `btcmi`, launch the API with:

```bash
uvicorn btcmi.api:app
```

## `POST /run`

Execute an analysis run. The payload must conform to `input_schema.json` and specify the desired mode (`v1` or `v2.fractal`).

### Example

```bash
curl -X POST http://localhost:8000/run \
  -H 'Content-Type: application/json' \
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
| 400  | unknown mode or validation fail |
| 500  | internal error                  |

## `POST /validate/{schema}`

Validate a payload against a registered schema (`input` or `output`).

### Example

```bash
curl -X POST http://localhost:8000/validate/input \
  -H 'Content-Type: application/json' \
  -d @examples/intraday.json
```

**Response**

```json
{"valid": true}
```

**Error codes**

| code | reason                |
|------|-----------------------|
| 400  | validation failed     |
| 404  | schema not found      |

## `GET /metrics`

Prometheus metrics endpoint.

### Example

```bash
curl http://localhost:8000/metrics
```

**Response**

```
btcmi_requests_total{endpoint="/run"} 1
```

**Error codes**

| code | reason             |
|------|--------------------|
| 500  | internal error     |

## `GET /healthz`

Simple health check.

### Example

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

