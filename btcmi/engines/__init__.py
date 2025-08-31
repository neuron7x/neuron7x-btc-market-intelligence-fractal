from __future__ import annotations

from functools import lru_cache

from .base import Engine, validate_scenario_window
from .v1 import EngineV1
from .v2 import EngineV2
from .nf3p import EngineNF3P


@lru_cache()
def load_engines() -> dict[str, Engine]:
    """Return mapping of mode names to engine instances."""
    return {
        "v1": EngineV1(),
        "v2.fractal": EngineV2(),
        "v2.nf3p": EngineNF3P(),
    }


__all__ = [
    "Engine",
    "EngineV1",
    "EngineV2",
    "EngineNF3P",
    "load_engines",
    "validate_scenario_window",
]
