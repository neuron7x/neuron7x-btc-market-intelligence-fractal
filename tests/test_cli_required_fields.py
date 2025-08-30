import pytest
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from btcmi.runner import run_v1, run_v2

R = Path(__file__).resolve().parents[1]
CLI = "cli.btcmi"

def test_run_v1_missing_scenario(tmp_path):
    data = {"window": "intraday"}
    with pytest.raises(ValueError, match="scenario"):
        run_v1(data, None, tmp_path / "out.json")


def test_run_v1_missing_window(tmp_path):
    data = {"scenario": "intraday"}
    with pytest.raises(ValueError, match="window"):
        run_v1(data, None, tmp_path / "out.json")


def test_run_v2_missing_scenario(tmp_path):
    data = {"window": "intraday"}
    with pytest.raises(ValueError, match="scenario"):
        run_v2(data, None, tmp_path / "out.json")


def test_run_v2_missing_window(tmp_path):
    data = {"scenario": "intraday"}
    with pytest.raises(ValueError, match="window"):
        run_v2(data, None, tmp_path / "out.json")


def test_run_v1_invalid_scenario(tmp_path):
    data = {"scenario": "invalid", "window": "intraday"}
    with pytest.raises(ValueError, match="scenario"):
        run_v1(data, None, tmp_path / "out.json")


def test_run_v2_invalid_scenario(tmp_path):
    data = {"scenario": "invalid", "window": "intraday"}
    with pytest.raises(ValueError, match="scenario"):
        run_v2(data, None, tmp_path / "out.json")


def test_validate_cli_returns_code_2(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "validate",
            "--schema",
            str(R / "input_schema.json"),
            "--data",
            str(invalid),
        ],
        capture_output=True,
    )
    assert result.returncode == 2
