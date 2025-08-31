"""BTC Market Intelligence package initialization."""

from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"
__version__ = VERSION_FILE.read_text().strip()

__all__ = [
    "engine_v1",
    "engine_v2",
    "engines",
    "logging_cfg",
    "schema_util",
    "utils",
]
