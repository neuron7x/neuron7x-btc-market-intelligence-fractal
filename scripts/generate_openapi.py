#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from fastapi.openapi.utils import get_openapi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from btcmi.api import app  # noqa: E402


def main() -> None:
    spec = get_openapi(
        title=app.title,
        version=getattr(app, "version", "0.1.0"),
        description=app.description,
        routes=app.routes,
    )
    out = ROOT / "docs" / "openapi.json"
    out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
