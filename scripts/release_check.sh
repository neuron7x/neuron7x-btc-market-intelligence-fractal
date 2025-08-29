#!/usr/bin/env bash
set -euo pipefail

# Run test suite including snapshots
pytest -q --disable-warnings --maxfail=1

# Verify SBOM exists
SBOM="provenance/sbom.spdx.json"
if [[ ! -f "$SBOM" ]]; then
  echo "Missing SBOM: $SBOM" >&2
  exit 1
fi

# Verify checksums file exists
CHECKSUMS="CHECKSUMS.SHA256"
if [[ ! -f "$CHECKSUMS" ]]; then
  echo "Missing checksums file: $CHECKSUMS" >&2
  exit 1
fi

# Validate checksums
python scripts/verify_checksums.py

# Ensure built artifacts are below 25MB
if [[ ! -d dist ]]; then
  echo "dist directory not found. Build artifacts before release." >&2
  exit 1
fi
for f in dist/*; do
  if [[ -f "$f" ]]; then
    size=$(stat -c%s "$f")
    if (( size >= 25*1024*1024 )); then
      echo "Artifact $f exceeds 25MB limit" >&2
      exit 1
    fi
  fi
fi

echo "Release checks passed."
