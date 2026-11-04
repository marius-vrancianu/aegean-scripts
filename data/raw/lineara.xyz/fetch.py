"""Fetch the pinned lineara.xyz snapshot and verify its hash.

The file has no licence (see DATA_SOURCES.md), so it is fetched, not committed.
Usage: python data/raw/lineara.xyz/fetch.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "9c81beba669a4ffec3f5b29d4e7748d02c060eff"
FILE = "LinearAInscriptions.js"
SHA256 = "9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e"
URL = f"https://raw.githubusercontent.com/mwenge/lineara.xyz/{COMMIT}/{FILE}"

dest = Path(__file__).resolve().parent / COMMIT[:12] / FILE


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if dest.exists() and sha256(dest) == SHA256:
        print(f"OK (cached): {dest}")
        return 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(URL, timeout=120) as r:
        tmp.write_bytes(r.read())
    got = sha256(tmp)
    if got != SHA256:
        tmp.unlink()
        print(f"HASH MISMATCH: expected {SHA256}, got {got}", file=sys.stderr)
        return 1
    tmp.replace(dest)
    print(f"OK: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
