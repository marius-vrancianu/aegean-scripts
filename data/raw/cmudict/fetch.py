"""Fetch the pinned cmudict.dict and verify its hash.

CMU Pronouncing Dictionary, BSD-style licence (see DATA_SOURCES.md). Fetched, not committed, to keep the repository small.
Usage: python data/raw/cmudict/fetch.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "74790861f652b15e4ac49015a90074ad62a27690"
FILE = "cmudict.dict"
REPO_PATH = "cmudict.dict"
SHA256 = "81917843c7f44ce2b094ac63873c2c7a4cf802040792c455ba3ca406891c3d22"
URL = f"https://raw.githubusercontent.com/cmusphinx/cmudict/{COMMIT}/{REPO_PATH}"

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
