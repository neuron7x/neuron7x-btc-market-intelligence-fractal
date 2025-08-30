import subprocess
import sys
from pathlib import Path


def run_script(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tests/validate_output.py", str(path)],
        capture_output=True,
        text=True,
    )


def test_validate_output_script_accepts_valid_file():
    valid = Path("tests/golden/intraday_v1.golden.json")
    result = run_script(valid)
    assert result.returncode == 0, result.stderr


def test_validate_output_script_rejects_invalid_file(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}")
    result = run_script(invalid)
    assert result.returncode != 0
    assert "Validation error" in result.stderr
