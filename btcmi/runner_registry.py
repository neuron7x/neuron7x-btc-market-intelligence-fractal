from __future__ import annotations

from functools import lru_cache
from importlib import metadata
from typing import Callable, Dict


@lru_cache()
def load_runners() -> Dict[str, Callable]:
    """Load runner implementations registered via ``btcmi.runners`` entry points.

    When the package is not installed with entry points (e.g. running from a
    source checkout), the built-in runners are loaded directly to provide a
    sensible default.

    Returns
    -------
    Dict[str, Callable]
        Mapping of runner mode names to callables.
    """
    eps = metadata.entry_points()
    try:
        selected = eps.select(group="btcmi.runners")
    except AttributeError:  # pragma: no cover - Python <3.10 compatibility
        selected = eps.get("btcmi.runners", [])
    registry = {ep.name: ep.load() for ep in selected}
    if not registry:  # fallback for source checkouts
        try:  # pragma: no cover - defensive
            from btcmi.runner import run_v1, run_v2

            registry = {"v1": run_v1, "v2.fractal": run_v2}
        except Exception:  # pragma: no cover - defensive
            registry = {}
    return registry


__all__ = ["load_runners"]
