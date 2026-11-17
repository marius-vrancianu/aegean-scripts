"""Fetch the pinned wordnet.zip and verify its hash.

Princeton WordNet 3.0 as packaged by NLTK; WordNet licence (see DATA_SOURCES.md). Fetched, not committed, to keep the repository small.
Usage: python data/raw/wordnet/fetch.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "550b6625bcef1f2abff2ff770a5a0d272c9c6b2a"
FILE = "wordnet.zip"
REPO_PATH = "packages/corpora/wordnet.zip"
SHA256 = "cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59"
URL = f"https://raw.githubusercontent.com/nltk/nltk_data/{COMMIT}/{REPO_PATH}"

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
