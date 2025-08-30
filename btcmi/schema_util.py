from pathlib import Path
import json


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def validate_json(data, schema_path):
    """Validate *data* against the JSON schema at *schema_path*.

    Requires the external ``jsonschema`` package. Install it with
    ``pip install jsonschema``.
    """

    schema = load_json(schema_path)
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:  # pragma: no cover - exercised in tests
        raise ImportError(
            "jsonschema is required for validate_json. Install with `pip install jsonschema`."
        ) from exc

    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(data), key=lambda e: e.path)
    if errors:
        msgs = []
        for e in errors:
            loc = "/".join(map(str, e.path))
            msgs.append(f"{loc}: {e.message}")
        raise ValueError("\n".join(msgs))
