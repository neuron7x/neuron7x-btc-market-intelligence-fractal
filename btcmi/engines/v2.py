from __future__ import annotations

from pathlib import Path
from typing import Any

from btcmi import runner
from btcmi.engines import register_engine


def run(
    data: dict[str, Any],
    fixed_ts: str | None,
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run the v2 fractal engine."""

    return runner.run_v2(data, fixed_ts, out_path)


register_engine("v2.fractal", run)

__all__ = ["run"]
