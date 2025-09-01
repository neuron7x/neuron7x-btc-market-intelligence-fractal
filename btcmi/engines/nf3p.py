from __future__ import annotations

from pathlib import Path
from typing import Any

from btcmi import runner


def run(
    data: dict[str, Any],
    fixed_ts: str | None,
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run the NF3P engine."""

    return runner.run_nf3p(data, fixed_ts, out_path)


__all__ = ["run"]
