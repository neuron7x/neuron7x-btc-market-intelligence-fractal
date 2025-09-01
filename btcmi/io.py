"""Input/output helpers for BTC Market Intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_output(data: dict[str, Any], out_path: Path | str) -> None:
    """Write ``data`` to ``out_path`` as JSON, creating parents if needed."""

    p = Path(out_path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError as e:  # pragma: no cover - handled by unit test
        raise RuntimeError(f"failed to write output to {out_path}: {e}") from e
