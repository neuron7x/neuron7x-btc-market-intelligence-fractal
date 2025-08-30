#!/usr/bin/env python3
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "provenance" / "sbom.spdx.json"
out.parent.mkdir(parents=True, exist_ok=True)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


files = []
for p in ROOT.rglob("*"):
    if p.is_file():
        files.append(
            {
                "fileName": str(p.relative_to(ROOT)),
                "checksums": [{"algorithm": "SHA256", "checksumValue": sha256(p)}],
                "fileSize": p.stat().st_size,
            }
        )
doc = {
    "spdxVersion": "SPDX-2.3",
    "name": "btcmi",
    "versionInfo": (ROOT / "VERSION").read_text().strip(),
    "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "files": files,
}
out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
print(out)
