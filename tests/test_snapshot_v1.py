import json
from pathlib import Path

import pytest

pytest.importorskip("syrupy")

from cli.btcmi import run_v1

R = Path(__file__).resolve().parents[1]


def test_v1_intraday(snapshot, tmp_path):
    """Compare v1 intraday output against stored snapshot."""
    data = json.loads((R / "examples" / "intraday.json").read_text())
    out = run_v1(data, "2025-01-01T00:00:00Z", tmp_path / "out.json")
    assert out == snapshot

