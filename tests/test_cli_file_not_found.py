import subprocess
import sys

import cli.btcmi as btcmi
from btcmi.schema_util import SCHEMA_REGISTRY

CLI = "cli.btcmi"


def test_run_cli_missing_input(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(tmp_path / "missing.json"),
            "--mode",
            "v1",
        ],
        capture_output=True,
    )
    assert result.returncode == 2
    assert b"input_file_not_found" in result.stderr


def test_validate_cli_missing_schema(tmp_path):
    data = tmp_path / "data.json"
    data.write_text("{}")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "validate",
            "--schema",
            str(tmp_path / "missing-schema.json"),
            "--data",
            str(data),
        ],
        capture_output=True,
    )
    assert result.returncode == 2
    assert b"schema_file_not_found" in result.stderr


def test_validate_cli_missing_data(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "validate",
            "--schema",
            str(SCHEMA_REGISTRY["input"]),
            "--data",
            str(tmp_path / "missing-data.json"),
        ],
        capture_output=True,
    )
    assert result.returncode == 2
    assert b"data_file_not_found" in result.stderr
