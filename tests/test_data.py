import json
from importlib.resources import files


def test_example_data_loads():
    path = files("btcmi").joinpath("examples/intraday.json")
    data = json.loads(path.read_text())
    assert data["mode"] == "v1"
