from __future__ import annotations

from pathlib import Path

from btcmi.engines import EngineV1, EngineV2, EngineNF3P
from btcmi.io import write_output


def run_v1(data, fixed_ts, out_path: str | Path | None = None):
    """Run the v1 engine and optionally persist the output."""
    return EngineV1().run(data, fixed_ts, out_path)


def run_v2(data, fixed_ts, out_path: str | Path | None = None):
    """Run the v2 fractal engine and optionally persist the output."""
    return EngineV2().run(data, fixed_ts, out_path)


def run_nf3p(data, fixed_ts, out_path: str | Path | None = None):
    """Run the NF3P engine and optionally persist the output."""
    return EngineNF3P().run(data, fixed_ts, out_path)


__all__ = ["run_v1", "run_v2", "run_nf3p", "write_output"]
