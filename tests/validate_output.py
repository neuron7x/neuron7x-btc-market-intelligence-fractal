import argparse
import json
import sys
from pathlib import Path

from jsonschema import ValidationError, validate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "output_schema.json"


def validate_output_file(output_path: Path) -> None:
    """Validate *output_path* against output_schema.json."""
    schema = json.loads(SCHEMA_PATH.read_text())
    data = json.loads(Path(output_path).read_text())
    validate(instance=data, schema=schema)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate output JSON against output_schema.json"
    )
    parser.add_argument("path", type=Path, help="path to generated output JSON file")
    args = parser.parse_args()

    try:
        validate_output_file(args.path)
    except ValidationError as err:  # pragma: no cover - sanity message
        print(f"Validation error: {err.message}", file=sys.stderr)
        sys.exit(1)
    print("Output is valid")


if __name__ == "__main__":
    main()
