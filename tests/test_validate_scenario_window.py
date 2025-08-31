import pytest

from btcmi.enums import Scenario, Window
from btcmi.engines import validate_scenario_window


def test_validate_returns_values():
    data = {"scenario": "intraday", "window": "1h"}
    scenario, window = validate_scenario_window(data)
    assert scenario is Scenario.INTRADAY
    assert window is Window.ONE_HOUR


def test_validate_missing_scenario():
    with pytest.raises(ValueError, match="scenario"):
        validate_scenario_window({"window": "1h"})


def test_validate_invalid_scenario():
    with pytest.raises(ValueError, match="scenario"):
        validate_scenario_window({"scenario": "invalid", "window": "1h"})


def test_validate_missing_window():
    with pytest.raises(ValueError, match="window"):
        validate_scenario_window({"scenario": "intraday"})
