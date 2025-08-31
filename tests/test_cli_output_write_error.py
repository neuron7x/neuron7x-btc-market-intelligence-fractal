import json
import subprocess
import sys
from pathlib import Path

CLI = "cli.btcmi"
R = Path(__file__).resolve().parents[1]


def test_run_cli_output_write_error(tmp_path):
    data = json.loads((R / "examples/intraday.json").read_text())
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(data))
    bad_parent = tmp_path / "notadir"
    bad_parent.write_text("file")
    out_path = bad_parent / "out.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "--json-errors",
            "run",
            "--input",
            str(inp),
            "--out",
            str(out_path),
            "--mode",
            "v1",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    parsed = json.loads(result.stdout)
    assert parsed["error"] == "output_write_failed"
    assert parsed["details"]["path"] == str(out_path)
    assert result.stderr == ""
