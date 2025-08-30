import json
import logging

from btcmi.logging_cfg import configure_logging, new_run_id


def test_json_log_format(capsys):
    configure_logging()
    logger = logging.getLogger("test")
    run_id = new_run_id()
    logger.info("hello", extra={"run_id": run_id, "mode": "test"})
    captured = capsys.readouterr()
    line = captured.err.strip()
    rec = json.loads(line)
    assert {"ts", "level", "msg", "run_id", "mode", "scenario"} <= set(rec.keys())
    assert rec["level"] == "info"
    assert rec["msg"] == "hello"
    assert rec["run_id"] == run_id
    assert rec["mode"] == "test"
    assert rec["scenario"] is None
    assert isinstance(rec["ts"], int)
