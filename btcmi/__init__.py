from pathlib import Path

__version__ = (Path(__file__).resolve().parent.parent / "VERSION").read_text().strip()
__all__ = ["engine_v1", "engine_v2", "logging_cfg", "schema_util", "utils"]
