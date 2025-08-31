"""BTC Market Intelligence package initialization."""

from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"
__version__ = VERSION_FILE.read_text().strip()

__all__ = [
    "data",
    "engine_v1",
    "engine_v2",
    "logging_cfg",
    "schema_util",
    "utils",
]
