"""Fetch the pinned tr_full.txt and verify its hash.

Turkish word frequencies from OpenSubtitles 2018; content CC BY-SA 4.0 (see DATA_SOURCES.md). Fetched, not committed (30 MB).
Usage: python data/raw/frequencywords/fetch.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "525f9b560de45753a5ea01069454e72e9aa541c6"
FILE = "tr_full.txt"
REPO_PATH = "content/2018/tr/tr_full.txt"
SHA256 = "62fed3d295a3250920f8a151f597cb28208633b6ff6e7bff90faed51ee86a9a5"
URL = f"https://raw.githubusercontent.com/hermitdave/FrequencyWords/{COMMIT}/{REPO_PATH}"

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
