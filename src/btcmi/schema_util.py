import json

# SCHEMA files live in the project root, two levels above ``src/btcmi``
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_REGISTRY = {
    "input": BASE_DIR / "input_schema.json",
    "output": BASE_DIR / "output_schema.json",
}

__all__ = ["load_json", "_load_schema", "validate_json", "SCHEMA_REGISTRY"]


_SCHEMA_CACHE: dict[str, dict] = {}


def load_json(path: str | Path) -> dict:
    """Load and parse JSON data from *path*.

    Parameters
    ----------
    path : str | Path
        Path to the JSON file to load.

    Returns
    -------
    dict
        Parsed JSON content.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    json.JSONDecodeError
        If the file contains invalid JSON.
    """

    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_schema(schema_path: str | Path) -> dict:
    """Load and cache the JSON schema located at *schema_path*.

    Parameters
    ----------
    schema_path : str | Path
        Path to the JSON schema file.

    Returns
    -------
    dict
        Parsed JSON schema.

    Raises
    ------
    FileNotFoundError
        If the schema file does not exist.
    json.JSONDecodeError
        If the schema file contains invalid JSON.
    """

    key = str(schema_path)
    schema = _SCHEMA_CACHE.get(key)
    if schema is None:
        schema = load_json(schema_path)
        _SCHEMA_CACHE[key] = schema
    return schema


def validate_json(data: dict, schema_path: str | Path) -> None:
    """Validate *data* against the JSON schema at *schema_path*.

    Requires the external ``jsonschema`` package. Install it with
    ``pip install jsonschema``.

    Parameters
    ----------
    data : dict
        JSON-like object to validate.
    schema_path : str | Path
        Path to the JSON schema to validate against.

    Raises
    ------
    ImportError
        If the ``jsonschema`` package is not installed.
    ValueError
        If *data* does not conform to the schema.
    FileNotFoundError
        If the schema file does not exist.
    json.JSONDecodeError
        If the schema file contains invalid JSON.
    """

    schema = _load_schema(schema_path)
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
