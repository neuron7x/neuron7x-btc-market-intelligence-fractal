"""Utility helpers for BTC Market Intelligence (BTCMI)."""

from numbers import Real


def is_number(x):
    """Return True if *x* is a real numeric value (excluding bool)."""
    return isinstance(x, Real) and not isinstance(x, bool)
