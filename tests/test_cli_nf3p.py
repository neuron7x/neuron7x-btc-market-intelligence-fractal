import json
import subprocess
import sys
import importlib.resources

CLI = "cli.btcmi"
f = importlib.resources.files("btcmi")


def test_cli_runs_nf3p(tmp_path):
    data = json.loads((f.joinpath("examples/intraday_fractal.json")).read_text())
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
