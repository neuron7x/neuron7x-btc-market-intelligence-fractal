import json
import pytest
import subprocess
import sys
from pathlib import Path

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


def test_run_cli_returns_code_2_on_invalid_input(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}")
    out = tmp_path / "out.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(invalid),
            "--out",
            str(out),
        ],
        capture_output=True,
    )
    assert result.returncode == 2


def test_run_cli_logs_validation_error(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}")
    out = tmp_path / "out.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(invalid),
            "--out",
            str(out),
        ],
        capture_output=True,
    )
    assert result.returncode == 2
    assert b"input_schema_validation_failed" in result.stderr


def test_run_cli_returns_code_2_on_missing_scenario(monkeypatch, tmp_path):
    data = {"schema_version": "2.0.0", "lineage": {}, "window": "1h"}
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(data))
    out = tmp_path / "out.json"
    monkeypatch.setattr("cli.btcmi.validate_json", lambda *a, **k: None)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(invalid),
            "--out",
            str(out),
        ],
        capture_output=True,
    )
    assert result.returncode == 2


def test_run_cli_returns_code_2_on_missing_window(monkeypatch, tmp_path):
    data = {"schema_version": "2.0.0", "lineage": {}, "scenario": "intraday"}
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(data))
    out = tmp_path / "out.json"
    monkeypatch.setattr("cli.btcmi.validate_json", lambda *a, **k: None)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(invalid),
            "--out",
            str(out),
        ],
        capture_output=True,
    )
    assert result.returncode == 2


def test_run_cli_prints_json_without_out():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(R / "examples/intraday.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["summary"]["scenario"] == "intraday"
