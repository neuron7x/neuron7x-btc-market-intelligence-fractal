from pathlib import Path
import json
def load_json(p): 
    return json.loads(Path(p).read_text(encoding="utf-8"))
def validate_json(data, schema_path):
    schema = load_json(schema_path)
    try:
        from jsonschema import Draft202012Validator
        v = Draft202012Validator(schema)
        errors = sorted(v.iter_errors(data), key=lambda e: e.path)
        if errors:
            msgs = []
            for e in errors:
                loc = "/".join(map(str, e.path))
                msgs.append(f"{loc}: {e.message}")
            raise ValueError("\n".join(msgs))
    except Exception:
        if schema.get("type") == "object" and not isinstance(data, dict):
            raise ValueError("root: must be object")
