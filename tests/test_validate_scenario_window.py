import pytest

from btcmi.runner import _validate_scenario_window


def test_validate_returns_values():
    data = {"scenario": "intraday", "window": "1h"}
    scenario, window = _validate_scenario_window(data)
    assert scenario == "intraday"
    assert window == "1h"


def test_validate_missing_scenario():
    with pytest.raises(ValueError, match="scenario"):
        _validate_scenario_window({"window": "1h"})


def test_validate_invalid_scenario():
    with pytest.raises(ValueError, match="scenario"):
        _validate_scenario_window({"scenario": "invalid", "window": "1h"})


def test_validate_missing_window():
    with pytest.raises(ValueError, match="window"):
        _validate_scenario_window({"scenario": "intraday"})
