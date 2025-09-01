"""Engine run wrappers and registry utilities."""

from __future__ import annotations

from typing import Callable, Dict

# Internal registry mapping engine names to callables.
ENGINE_REGISTRY: Dict[str, Callable] = {}


def register_engine(name: str, engine_cls: Callable) -> None:
    """Register an engine implementation under ``name``.

    Parameters
    ----------
    name:
        The mode name exposed to ``load_runners``.
    engine_cls:
        Callable object (typically a ``run`` function) implementing the engine.
    """

    ENGINE_REGISTRY[name] = engine_cls


# Import built-in engines so they self-register.
from . import v1 as v1  # noqa: F401  # side-effect: registers engine
from . import v2 as v2  # noqa: F401  # side-effect: registers engine
from . import nf3p as nf3p  # noqa: F401  # side-effect: registers engine
from . import base as base  # noqa: F401

__all__ = [
    "register_engine",
    "ENGINE_REGISTRY",
    "base",
    "v1",
    "v2",
    "nf3p",
]
