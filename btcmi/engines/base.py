from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

from btcmi.enums import Scenario, Window


def validate_scenario_window(data: Dict[str, Any]) -> Tuple[Scenario, Window]:
    """Return the scenario and window ensuring both are valid."""
    scenario = data.get("scenario")
    if scenario is None:
        raise ValueError("'scenario' field is required")
    try:
        scenario_enum = scenario if isinstance(scenario, Scenario) else Scenario(scenario)
    except ValueError as exc:  # pragma: no cover - defensive
        allowed = ", ".join(sorted(s.value for s in Scenario))
        raise ValueError("'scenario' must be one of: " + allowed) from exc

    window = data.get("window")
    if window is None:
        raise ValueError("'window' field is required")
    try:
        window_enum = window if isinstance(window, Window) else Window(window)
    except ValueError as exc:  # pragma: no cover - defensive
        allowed = ", ".join(sorted(w.value for w in Window))
        raise ValueError("'window' must be one of: " + allowed) from exc
    return scenario_enum, window_enum


class Engine(ABC):
    """Abstract base class for BTCMI engines."""

    _validate_scenario_window = staticmethod(validate_scenario_window)

    @abstractmethod
    def run(self, data: Dict[str, Any], fixed_ts, out_path):
        """Run the engine and return results."""
        raise NotImplementedError
