from __future__ import annotations

from pathlib import Path
from typing import Any

from btcmi import runner


def run(
    self: Any,
    data: dict[str, Any],
    fixed_ts: str | None,
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    """Dispatch to the appropriate engine based on ``data['mode']``."""

    mode = data.get("mode")
    if mode == "v2.fractal":
        return runner.run_v2(data, fixed_ts, out_path)
    if mode == "v2.nf3p":
        return runner.run_nf3p(data, fixed_ts, out_path)
    return runner.run_v1(data, fixed_ts, out_path)


__all__ = ["run"]
