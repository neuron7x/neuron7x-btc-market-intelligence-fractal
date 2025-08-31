"""Utility helpers for BTC Market Intelligence (BTCMI)."""

from numbers import Real
from typing import Any


def is_number(x: Any) -> bool:
    """Return True if *x* is a real numeric value (excluding bool)."""
    return isinstance(x, Real) and not isinstance(x, bool)
