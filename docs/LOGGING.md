# Logging configuration

BTCMI uses structured JSON logging powered by
[`python-json-logger`](https://github.com/madzak/python-json-logger). Each log
record contains a timestamp (`ts`), level, message, `run_id`, `mode` and
`scenario` fields to help correlate activity across components.

## CLI example

```bash
$ LOG_LEVEL=DEBUG btcmi run --input sample.json --mode v1
{"ts": 1700000000000, "level": "info", "msg": "run_ok", "run_id": "…", "mode": "v1", "scenario": "baseline"}
```

## FastAPI example

```python
from btcmi.logging_cfg import configure_logging

configure_logging()
# proceed to start the application, e.g. with uvicorn
```

Run the API:

```bash
$ uvicorn btcmi.api:app
```

Setting the `LOG_LEVEL` environment variable controls verbosity:

```bash
$ LOG_LEVEL=WARNING uvicorn btcmi.api:app
```

