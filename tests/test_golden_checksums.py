import hashlib
from pathlib import Path

GOLDEN = Path(__file__).resolve().parent / "golden"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def test_golden_files_checksums():
    checksums = (GOLDEN / "CHECKSUMS.SHA256").read_text().splitlines()
    for line in checksums:
        if not line.strip():
            continue
        want, name = line.split()
        got = _sha256(GOLDEN / name)
        assert got == want, f"checksum mismatch for {name}"
