from pathlib import Path
import json
from json import JSONDecodeError


_SCHEMA_CACHE: dict[str, dict] = {}
_VALIDATOR_CACHE: dict[str, "Draft202012Validator"] = {}


def load_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSON file not found: {p}") from exc
    except JSONDecodeError as exc:
        raise JSONDecodeError(
            f"Invalid JSON in {p}: {exc.msg}", exc.doc, exc.pos
        ) from exc


def _load_schema(schema_path):
    key = str(schema_path)
    schema = _SCHEMA_CACHE.get(key)
    if schema is None:
        schema = load_json(schema_path)
        _SCHEMA_CACHE[key] = schema
    return schema


def validate_json(data, schema_path):
    """Validate *data* against the JSON schema at *schema_path*.

    Requires the external ``jsonschema`` package. Install it with
    ``pip install jsonschema``.
    """

    key = str(schema_path)
    validator = _VALIDATOR_CACHE.get(key)
    if validator is None:
        schema = _load_schema(schema_path)
        try:
            from jsonschema import Draft202012Validator
        except ImportError as exc:  # pragma: no cover - exercised in tests
            raise ImportError(
                "jsonschema is required for validate_json. Install with `pip install jsonschema`."
            ) from exc
        validator = Draft202012Validator(schema)
        _VALIDATOR_CACHE[key] = validator

    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        msgs = []
        for e in errors:
            loc = "/".join(map(str, e.path))
            msgs.append(f"{loc}: {e.message}")
        raise ValueError("\n".join(msgs))
