#!/usr/bin/env python3
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks = ROOT / "CHECKSUMS.SHA256"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


if not checks.exists():
    print("No CHECKSUMS.SHA256 found; skipping", file=sys.stderr)
    sys.exit(0)

bad = False
for line in checks.read_text().splitlines():
    if not line.strip():
        continue
    want, rel = line.split(maxsplit=1)
    p = ROOT / rel.strip()
    if not p.exists():
        print(f"MISSING {rel}", file=sys.stderr)
        bad = True
        continue
    got = sha256(p)
    if got != want:
        print(f"SHA MISMATCH {rel}", file=sys.stderr)
        bad = True
print("CHECKSUMS OK" if not bad else "CHECKSUMS FAIL")
sys.exit(2 if bad else 0)
