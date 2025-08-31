"""BTC Market Intelligence package initialization."""

from pathlib import Path

# project root is two levels above ``src/btcmi``
VERSION_FILE = Path(__file__).resolve().parents[2] / "VERSION"
__version__ = VERSION_FILE.read_text().strip()

__all__ = [
    "engine_v1",
    "engine_v2",
    "logging_cfg",
    "schema_util",
    "utils",
]
