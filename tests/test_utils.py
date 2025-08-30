import sys
from pathlib import Path
from decimal import Decimal
from fractions import Fraction

import pytest


# Allow tests to import the project modules directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from btcmi.utils import is_number


@pytest.mark.parametrize(
    "val",
    [1, 1.0, 1 + 2j, Decimal("1.23"), Fraction(1, 3)],
)
def test_is_number_with_numeric_types(val):
    """``is_number`` should return True for standard numeric objects."""
    assert is_number(val)


@pytest.mark.parametrize("val", [True, False, "1", None, [], object()])
def test_is_number_with_non_numeric_types(val):
    """``is_number`` should return False for non-numeric objects."""
    assert not is_number(val)

