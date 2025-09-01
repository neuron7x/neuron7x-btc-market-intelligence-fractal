"""Engine run wrappers and type definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


Engine = Callable[[dict[str, Any], str | None, str | Path | None], dict[str, Any]]


__all__ = ["Engine", "base", "v1", "v2", "nf3p"]
