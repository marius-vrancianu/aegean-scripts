"""Fetch the pinned linear_b-greek.cog and verify its hash.

The NeuroDecipher repository states no licence (see DATA_SOURCES.md), so the file is fetched, not committed.
Usage: python data/raw/neurodecipher/fetch.py
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "480bad2487820e3737fecfdd108214efa769e34b"
FILE = "linear_b-greek.cog"
REPO_PATH = "data/linear_b-greek.cog"
SHA256 = "0e8099cd9f02c36fc14599d9bc12836489816c0b1d17f471e723b98c978b10fa"
URL = f"https://raw.githubusercontent.com/j-luo93/NeuroDecipher/{COMMIT}/{REPO_PATH}"

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
