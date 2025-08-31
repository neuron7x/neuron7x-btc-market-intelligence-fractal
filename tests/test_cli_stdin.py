import io
import json
import sys
from pathlib import Path

import cli.btcmi as btcmi

R = Path(__file__).resolve().parents[1]


def test_run_cli_reads_from_stdin(monkeypatch, capsys):
    data = (R / "btcmi/examples/intraday.json").read_text()
    monkeypatch.setattr(sys, "argv", ["btcmi", "run", "--input", "-", "--mode", "v1"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(data))
    code = btcmi.main()
    captured = capsys.readouterr()
    assert code == 0
    parsed = json.loads(captured.out)
    assert parsed["summary"]["scenario"] == "intraday"


def test_run_cli_invalid_payload_from_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["btcmi", "run", "--input", "-", "--mode", "v1"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("{}"))
    code = btcmi.main()
    captured = capsys.readouterr()
    assert code == 2
    assert "input_schema_validation_failed" in captured.err
