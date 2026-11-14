"""Fetch the pinned HebrewStrong.xml and verify its hash.

CC BY 4.0 (see DATA_SOURCES.md). Fetched, not committed, to keep the repository small; same cache path as experiments/finding-001/reproduce.py.
Usage: python data/raw/openscriptures-HebrewLexicon/fetch.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "21c9add13bc727d3a951361778e97e3ff7afd1ce"
FILE = "HebrewStrong.xml"
REPO_PATH = "HebrewStrong.xml"
SHA256 = "a628f4f89f8bdaf2483fd3faf1abc8653cc6717758dfc9f24beb7571d9bdd0c4"
URL = f"https://raw.githubusercontent.com/openscriptures/HebrewLexicon/{COMMIT}/{REPO_PATH}"

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
