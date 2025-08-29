# Snapshot Updates

The API regression tests compare responses against snapshot files in `tests/golden`.
If you intentionally change the API output, regenerate the snapshots with:

```bash
UPDATE_SNAPSHOTS=1 pytest tests/test_api_snapshots.py
```

The updated files will be written to:

- `tests/golden/api_run_v1.golden.json`
- `tests/golden/api_run_v2.golden.json`
