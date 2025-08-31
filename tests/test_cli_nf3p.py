import json
import subprocess
import sys
from pathlib import Path

CLI = "cli.btcmi"
R = Path(__file__).resolve().parents[1]


def test_cli_runs_nf3p(tmp_path):
    data = json.loads((R / "examples/intraday_fractal.json").read_text())
    data["mode"] = "v2.nf3p"
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(data))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            CLI,
            "run",
            "--input",
            str(inp),
            "--mode",
            "v2.nf3p",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert "predictions" in out
    assert "backtest" in out
