import pandas as pd
import pytest
from pathlib import Path

from btcmi.data import load_ohlcv, validate_ohlcv


@pytest.fixture
def ohlcv_csv_path() -> Path:
    return Path("examples/ohlcv.csv")


@pytest.fixture
def ohlcv_json_path() -> Path:
    return Path("examples/ohlcv.json")


def test_load_csv(ohlcv_csv_path: Path):
    df = load_ohlcv(ohlcv_csv_path)
    assert df.shape == (3, 6)
    validate_ohlcv(df)


def test_load_json(ohlcv_json_path: Path):
    df = load_ohlcv(ohlcv_json_path)
    assert df.shape == (3, 6)
    validate_ohlcv(df)


def test_validate_missing_column():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01T00:00:00Z"],
        "open": [1],
        "high": [1],
        "low": [1],
        "close": [1],
        # volume missing
    })
    with pytest.raises(ValueError):
        validate_ohlcv(df)


def test_validate_non_numeric():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01T00:00:00Z"],
        "open": ["bad"],
        "high": [1],
        "low": [1],
        "close": [1],
        "volume": [1],
    })
    with pytest.raises(TypeError):
        validate_ohlcv(df)
