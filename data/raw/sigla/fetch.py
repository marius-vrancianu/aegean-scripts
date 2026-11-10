"""Fetch the SigLA database snapshot and verify it against SHA256SUMS.

SigLA is CC BY-NC-SA 4.0 (Salgarella & Castellan), so the snapshot itself is
committed (DATA_SOURCES.md). This script exists so the snapshot can be
re-fetched and compared; if the live file has changed, the hash check fails,
which means a new snapshot directory and a new SHA256SUMS line, never an edit
to the pinned one.

Held-out check: the pinned snapshot has no record of the documents in
data/heldout.txt (checked by document ID only). `aegean.corpus.sigla` still
filters through data/heldout.txt at ingest.

Usage: python data/raw/sigla/fetch.py            # verify the committed snapshot
       python data/raw/sigla/fetch.py --download # re-download and verify
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

URL = "https://sigla.phis.me/database.js"
HERE = Path(__file__).resolve().parent
SUMS = HERE / "SHA256SUMS"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned() -> dict[str, str]:
    """{relative path: sha256} from SHA256SUMS (sha256sum format)."""
    out = {}
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            digest, rel = line.split(maxsplit=1)
            out[rel.lstrip("*")] = digest
    return out


def main(argv: list[str]) -> int:
    sums = pinned()
    if "--download" in argv:
        with urllib.request.urlopen(URL, timeout=120) as r:
            data = r.read()
        got = hashlib.sha256(data).hexdigest()
        rel = next((p for p, d in sums.items() if d == got), None)
        if rel is None:
            print(f"Live file differs from every pinned snapshot (sha256 {got}). "
                  "Make a new snapshot directory; do not overwrite.", file=sys.stderr)
            return 1
        print(f"OK: live file matches pinned {rel}")
        return 0
    status = 0
    for rel, digest in sums.items():
        path = HERE / rel
        if not path.exists():
            print(f"MISSING: {rel}", file=sys.stderr)
            status = 1
        elif (got := sha256(path)) != digest:
            print(f"HASH MISMATCH: {rel}: expected {digest}, got {got}", file=sys.stderr)
            status = 1
        else:
            print(f"OK: {rel}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
