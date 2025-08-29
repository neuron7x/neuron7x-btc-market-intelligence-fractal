from __future__ import annotations

import json
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

from btcmi.schema_util import load_json, validate_json


class Adapter(ABC):
    """Abstract adapter interface for external IO."""

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Retrieve input payload."""

    @abstractmethod
    def validate(self, data: Dict[str, Any], schema: Path) -> None:
        """Validate payload against a JSON schema."""

    @abstractmethod
    def emit(self, data: Dict[str, Any]) -> None:
        """Persist or transmit the payload."""


class FileAdapter(Adapter):
    """Adapter working with local JSON files."""

    def __init__(self, input_path: Path, output_path: Path | None = None) -> None:
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else None

    def load(self) -> Dict[str, Any]:
        return load_json(self.input_path)

    def validate(self, data: Dict[str, Any], schema: Path) -> None:
        validate_json(data, schema)

    def emit(self, data: Dict[str, Any]) -> None:
        if not self.output_path:
            raise ValueError("output_path not set")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class APIAdapter(Adapter):
    """Example adapter interacting with an HTTP API."""

    def __init__(self, url: str) -> None:
        self.url = url

    def load(self) -> Dict[str, Any]:
        with urllib.request.urlopen(self.url) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def validate(self, data: Dict[str, Any], schema: Path) -> None:
        validate_json(data, schema)

    def emit(self, data: Dict[str, Any]) -> None:
        req = urllib.request.Request(
            self.url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req)
