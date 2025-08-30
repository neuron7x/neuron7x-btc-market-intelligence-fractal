"""NF3P variant 2 signal engine.

This module provides a light‑weight reference implementation of the
``NF3P`` (Non‑linear Fractal‑based Price Prediction) engine.  The class is
intentionally minimalist but exposes a familiar ``scikit‑learn`` style API
via ``fit`` and ``predict`` methods alongside helper utilities used in
trading research such as ``size_positions``, ``backtest`` and
``walk_forward``.

Several of the feature extraction techniques employed in fractal based
analysis – Detrended Fluctuation Analysis (DFA), Multi Fractal DFA (MFDFA)
and Approximate Entropy (ApEn) – can be extremely expensive for long time
series.  To keep the engine responsive during unit tests and light weight
experiments the heavy loops implementing those techniques are wrapped in
optional code paths.  By default they are disabled and only cheap summary
statistics are computed.  They may be enabled when needed by passing the
appropriate flags to :class:`Variant2`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Helper feature functions
# ---------------------------------------------------------------------------

def dfa(series: Sequence[float], window: int = 5) -> float:
    """Compute a tiny DFA score.

    The implementation is intentionally naive and uses explicit Python loops
    so that the function acts as a stand in for a much heavier routine.  It
    is adequate for tests and small research examples but should not be used
    for production analytics.
    """

    n = len(series)
    if n < window:
        return 0.0
    vals: List[float] = []
    x = np.arange(window)
    for i in range(0, n - window + 1):
        seg = np.array(series[i : i + window])
        coeffs = np.polyfit(x, seg, 1)
        trend = np.polyval(coeffs, x)
        vals.append(float(np.sqrt(np.mean((seg - trend) ** 2))))
    return float(np.mean(vals)) if vals else 0.0


def mfdfa(series: Sequence[float], q: int = 2, window: int = 5) -> float:
    """Compute a toy MFDFA score using nested loops.

    Similar to :func:`dfa` this routine is not intended to be accurate but to
    emulate the computational cost of the genuine algorithm when the feature
    path is enabled.
    """

    n = len(series)
    if n < window:
        return 0.0
    vals: List[float] = []
    x = np.arange(window)
    for i in range(0, n - window + 1):
        seg = np.array(series[i : i + window])
        coeffs = np.polyfit(x, seg, 1)
        trend = np.polyval(coeffs, x)
        fluct = np.mean(np.abs(seg - trend) ** q) ** (1.0 / q)
        vals.append(float(fluct))
    return float(np.mean(vals)) if vals else 0.0


def approximate_entropy(series: Sequence[float], m: int = 2, r: float = 0.2) -> float:
    """Return a simple approximate entropy statistic.

    This is a minimal re‑implementation of the classical ApEn algorithm.  It
    is deliberately verbose and uses explicit loops to highlight its cost.
    """

    n = len(series)
    if n <= m + 1:
        return 0.0
    def _phi(m: int) -> float:
        patterns: List[Sequence[float]] = [series[i : i + m] for i in range(n - m + 1)]
        C: List[int] = []
        for p in patterns:
            count = 0
            for q in patterns:
                if max(abs(np.array(p) - np.array(q))) <= r:
                    count += 1
            C.append(count / (n - m + 1))
        return float(np.mean(np.log(C)))
    return _phi(m) - _phi(m + 1)


# ---------------------------------------------------------------------------
# Variant 2 engine
# ---------------------------------------------------------------------------

@dataclass
class Variant2:
    """Minimal NF3P variant 2 engine.

    Parameters control whether expensive fractal features are computed.
    By default only mean and standard deviation statistics are extracted.
    """

    use_dfa: bool = False
    use_mfdfa: bool = False
    use_apen: bool = False

    def fit(self, series: Sequence[float]) -> "Variant2":
        """Extract features from ``series``.

        Heavy feature calculations are included only if the corresponding
        boolean flag was enabled at initialisation.
        """

        arr = np.asarray(series, dtype=float)
        self.features_ = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)) if len(arr) > 1 else 0.0,
        }
        if self.use_dfa:
            self.features_["dfa"] = dfa(arr)
        if self.use_mfdfa:
            self.features_["mfdfa"] = mfdfa(arr)
        if self.use_apen:
            self.features_["apen"] = approximate_entropy(arr)
        self.is_fitted_ = True
        return self

    # ------------------------------------------------------------------
    def predict(self, series: Sequence[float]) -> float:
        """Generate a simple directional prediction for ``series``.

        The final observation is compared against the mean of the training
        window producing either ``1`` for momentum or ``-1`` for mean reversion.
        """

        if not getattr(self, "is_fitted_", False):
            raise RuntimeError("Call 'fit' before 'predict'.")
        arr = np.asarray(series, dtype=float)
        if len(arr) == 0:
            return 0.0
        return 1.0 if arr[-1] >= self.features_.get("mean", 0.0) else -1.0

    # ------------------------------------------------------------------
    def size_positions(self, signal: float, capital: float = 1.0) -> float:
        """Return the position size implied by ``signal``.

        ``signal`` is expected in the range [-1, 1].  The returned value is
        clipped so that the absolute exposure never exceeds ``capital``.
        """

        size = capital * float(signal)
        return float(max(-capital, min(capital, size)))

    # ------------------------------------------------------------------
    def backtest(self, series: Sequence[float]) -> Tuple[List[float], List[float]]:
        """Naive in-sample backtest over ``series``.

        For each time step the model is fit on all data up to ``t`` and a
        prediction is generated for ``t+1``.  PnL is computed using simple
        differenced returns.
        """

        preds: List[float] = []
        pnl: List[float] = []
        for i in range(1, len(series)):
            window = series[:i]
            self.fit(window)
            signal = self.predict(window)
            preds.append(signal)
            pnl.append(signal * (series[i] - series[i - 1]))
        return preds, pnl

    # ------------------------------------------------------------------
    def walk_forward(
        self, series: Sequence[float], window: int
    ) -> Tuple[List[float], List[float]]:
        """Walk-forward evaluation over ``series`` using ``window`` size."""

        preds: List[float] = []
        pnl: List[float] = []
        for i in range(window, len(series)):
            hist = series[i - window : i]
            self.fit(hist)
            signal = self.predict(hist)
            preds.append(signal)
            pnl.append(signal * (series[i] - series[i - 1]))
        return preds, pnl


# ---------------------------------------------------------------------------
# Convenience module level wrappers
# ---------------------------------------------------------------------------

def fit(series: Sequence[float], **kwargs) -> Variant2:
    """Fit a :class:`Variant2` model on ``series`` and return the instance."""

    return Variant2(**kwargs).fit(series)


def predict(model: Variant2, series: Sequence[float]) -> float:
    """Wrapper calling :meth:`Variant2.predict`."""

    return model.predict(series)


def size_positions(model: Variant2, signal: float, capital: float = 1.0) -> float:
    """Wrapper for :meth:`Variant2.size_positions`."""

    return model.size_positions(signal, capital)


def backtest(model: Variant2, series: Sequence[float]) -> Tuple[List[float], List[float]]:
    """Wrapper around :meth:`Variant2.backtest`."""

    return model.backtest(series)


def walk_forward(
    model: Variant2, series: Sequence[float], window: int
) -> Tuple[List[float], List[float]]:
    """Wrapper for :meth:`Variant2.walk_forward`."""

    return model.walk_forward(series, window)


__all__ = [
    "Variant2",
    "dfa",
    "mfdfa",
    "approximate_entropy",
    "fit",
    "predict",
    "size_positions",
    "backtest",
    "walk_forward",
]
