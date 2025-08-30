from __future__ import annotations

from typing import Callable, Dict

from btcmi.runner import run_v1, run_v2


# type alias for clarity
Runner = Callable[[dict, str | None,], dict]


def load_runners() -> Dict[str, Callable]:
    """Return mapping of available runners.

    This indirection allows tests to patch this function to supply custom
    runner implementations without mutating global state.
    """
    return {
        "v1": run_v1,
        "v2.fractal": run_v2,
    }
