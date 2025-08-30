from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import entry_points

from btcmi.runner import run_v1, run_v2


def load_runners() -> dict[str, Callable]:
    """Load runner implementations from entry points.

    The group ``btcmi.runners`` is inspected and all discovered entry points are
    loaded.  When no entry points are found the built-in runners are returned to
    maintain backwards compatibility.
    """
    try:
        eps = entry_points()
        if hasattr(eps, "select"):
            group = eps.select(group="btcmi.runners")
        else:  # pragma: no cover - legacy importlib
            group = eps.get("btcmi.runners", [])
    except Exception:  # pragma: no cover - defensive
        group = []
    runners = {ep.name: ep.load() for ep in group}
    if not runners:
        runners = {"v1": run_v1, "v2.fractal": run_v2}
    return runners


RUNNERS = load_runners()

__all__ = ["RUNNERS", "load_runners"]
