import hashlib
from pathlib import Path


def sha256sum(path: Path) -> str:
    """Return SHA256 hex digest for file at path."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_schema_freeze():
    repo_root = Path(__file__).resolve().parent.parent
    expected_hashes = {
        "input_schema.json": "73785babd0d0ccfecea421af95b27b35c4f71049fb2e5fec3e5cbc94ea892203",
        "output_schema.json": "ad2a0f1f7933df91faf09eb76ca7bbf566913c7a200694ca4b03b9e0effdbac3",
    }
    for filename, expected in expected_hashes.items():
        file_hash = sha256sum(repo_root / filename)
        assert (
            file_hash == expected
        ), f"{filename} hash changed: {file_hash} != {expected}"
