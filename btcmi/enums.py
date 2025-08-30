from __future__ import annotations

from enum import Enum


class Scenario(str, Enum):
    INTRADAY = "intraday"
    SCALP = "scalp"
    SWING = "swing"


class Window(str, Enum):
    ONE_HOUR = "1h"
    ONE_DAY = "1d"


__all__ = ["Scenario", "Window"]
