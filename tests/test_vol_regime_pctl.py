import pytest

from btcmi.runner import run_v2

BASE_DATA = {"scenario": "intraday", "window": "1h"}


@pytest.mark.parametrize("pctl, regime", [(0.0, "low"), (1.0, "high")])
def test_run_v2_vol_regime_pctl_boundaries(pctl, regime):
    data = dict(BASE_DATA, vol_regime_pctl=pctl)
    out = run_v2(data, None)
    assert out["details"]["router_regime"] == regime


@pytest.mark.parametrize("pctl", [-0.1, 1.1])
def test_run_v2_vol_regime_pctl_invalid(pctl):
    data = dict(BASE_DATA, vol_regime_pctl=pctl)
    with pytest.raises(ValueError, match="vol_regime_pctl"):
        run_v2(data, None)


def test_run_v2_vol_regime_pctl_non_numeric():
    data = dict(BASE_DATA, vol_regime_pctl="invalid")
    with pytest.raises(ValueError, match="vol_regime_pctl"):
        run_v2(data, None)
