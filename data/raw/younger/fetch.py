"""Verify the manually downloaded Younger files against SHA256SUMS.

Younger's files are on Academia.edu, which needs a login and blocks automated
access, so they cannot be fetched by script. They have no stated licence, so
they are not committed. To reproduce: download them by hand from the URLs in
README.md into data/raw/younger/academia-2024/ under the file names listed in
SHA256SUMS, then run this script. A hash mismatch means a different version
(Academia allows re-uploads): record it as a new snapshot, never overwrite.

Usage: python data/raw/younger/fetch.py
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMS = HERE / "SHA256SUMS"


def main() -> int:
    status = 0
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(maxsplit=1)
        path = HERE / rel.lstrip("*")
        if not path.exists():
            print(f"MISSING: {rel} (download it by hand; see README.md)", file=sys.stderr)
            status = 1
            continue
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != digest:
            print(f"HASH MISMATCH: {rel}: expected {digest}, got {got}", file=sys.stderr)
            status = 1
        else:
            print(f"OK: {rel}")
    return status


if __name__ == "__main__":
    sys.exit(main())
