import pytest
from pathlib import Path

from btcmi import runner


def test_write_output_raises_runtime_error(monkeypatch, tmp_path):
    out_file = tmp_path / "out.json"

    def fake_write_text(self, *args, **kwargs):
        raise OSError("mock failure")

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    with pytest.raises(RuntimeError) as exc:
        runner.write_output({"foo": "bar"}, out_file)
    assert f"failed to write output to {out_file}" in str(exc.value)
