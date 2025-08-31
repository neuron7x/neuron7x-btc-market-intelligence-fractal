"""Data utilities for loading and validating OHLCV candle data."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Union

import pandas as pd

# Required columns for OHLCV candle datasets
REQUIRED_COLUMNS: Iterable[str] = ("timestamp", "open", "high", "low", "close", "volume")


def load_ohlcv(path: Union[str, Path]) -> pd.DataFrame:
    """Load OHLCV candles from *path*.

    The function supports CSV and JSON files and returns a ``pandas.DataFrame``
    containing the candles. The ``timestamp`` column is parsed into
    ``datetime64[ns, UTC]`` dtype. The resulting dataframe is validated using
    :func:`validate_ohlcv` before being returned.

    Parameters
    ----------
    path:
        Path to the CSV or JSON file containing OHLCV candles.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the loaded OHLCV candles.
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".json":
        # ``pd.read_json`` can consume a file path directly. The JSON is
        # expected to be either a list of objects or records orientation.
        df = pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file extension: {suffix}")

    # Parse timestamps if present
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    validate_ohlcv(df)
    return df


def validate_ohlcv(df: pd.DataFrame) -> None:
    """Validate an OHLCV dataframe.

    The dataframe must contain the required columns and those columns (except
    ``timestamp``) must be numeric and free of missing values. ``timestamp``
    values must also be non-null.

    Parameters
    ----------
    df:
        DataFrame to validate.

    Raises
    ------
    ValueError
        If required columns are missing or contain null values.
    TypeError
        If price/volume columns are not numeric.
    """

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    # ``timestamp`` column must not contain null values
    if df["timestamp"].isnull().any():
        raise ValueError("Column 'timestamp' contains null values")

    # Ensure numeric columns are numeric and non-null
    for col in REQUIRED_COLUMNS[1:]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise TypeError(f"Column '{col}' must be numeric")
        if df[col].isnull().any():
            raise ValueError(f"Column '{col}' contains null values")

