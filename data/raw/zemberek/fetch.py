"""Fetch the pinned master-dictionary.dict and verify its hash.

Zemberek-NLP Turkish dictionary, Apache-2.0 (see DATA_SOURCES.md). Fetched, not committed: the list's own provenance (probably the TDK dictionary) is unverified.
Usage: python data/raw/zemberek/fetch.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "fd8c674927f0c86dc4c09429e6dbc4f6f4abd924"
FILE = "master-dictionary.dict"
REPO_PATH = "morphology/src/main/resources/tr/master-dictionary.dict"
SHA256 = "7eec0b78ca39c243e665bb1001eaaa6bda3a8dc86773e736d3a21fc9eb1c4c23"
URL = f"https://raw.githubusercontent.com/ahmetaa/zemberek-nlp/{COMMIT}/{REPO_PATH}"

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
