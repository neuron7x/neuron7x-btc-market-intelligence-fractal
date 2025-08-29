import json
import pytest
from btcmi.schema_util import validate_json

def test_validate_json_additional_properties(tmp_path):
    pytest.importorskip("jsonschema")
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"foo": {"type": "string"}},
        "required": ["foo"],
        "additionalProperties": False,
    }
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(schema))
    data = {"foo": "bar", "extra": "baz"}
    with pytest.raises(ValueError):
        validate_json(data, schema_path)
