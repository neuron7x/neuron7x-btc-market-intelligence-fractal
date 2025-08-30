"""Utility helpers for BTC Market Intelligence (BTCMI)."""

from numbers import Number


def is_number(x):
    """Return True if *x* is a numeric value (excluding bool)."""
    return isinstance(x, Number) and not isinstance(x, bool)

