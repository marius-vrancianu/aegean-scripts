"""Verify Younger's files against SHA256SUMS, optionally copying them in first.

Younger's files are on Academia.edu, which needs a login and blocks automated
access. They have no stated licence, so they are not committed to this public
repository. Marius keeps a copy in a private repository,
marius-vrancianu/aegean-scripts-private (folder Younger/).

In a session:
  1. attach and clone that repository (read access is enough);
  2. python data/raw/younger/fetch.py --from <clone>/Younger

--from copies the files named in SHA256SUMS into data/raw/younger/academia-2024/
(gitignored) and then verifies them. Without --from, the script only verifies
what is already there. A file whose hash differs is never copied over an
existing one: a different version (Academia allows re-uploads) is a new
snapshot and gets its own folder and SHA256SUMS entries.

Do not attach these files to a chat and do not add them to the claude.ai
Project: they contain the texts of held-out documents, and either route puts
them into a session's context (CLAUDE.md, held-out material).
"""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMS = HERE / "SHA256SUMS"


def entries() -> list[tuple[str, str]]:
    out = []
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            digest, rel = line.split(maxsplit=1)
            out.append((digest, rel.lstrip("*")))
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_from(source: Path) -> int:
    """Copy each pinned file from `source` (flat folder) if its hash matches. Returns the number of problems."""
    problems = 0
    for digest, rel in entries():
        src, dest = source / Path(rel).name, HERE / rel
        if not src.exists():
            print(f"NOT IN SOURCE: {src.name}", file=sys.stderr)
            continue  # verification below reports it as MISSING if it is not already present
        if sha256(src) != digest:
            print(f"HASH MISMATCH in source: {src.name} is a different version; not copied", file=sys.stderr)
            problems += 1
            continue
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            print(f"copied: {rel}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="source", type=Path, metavar="DIR",
                    help="folder holding the files (the Younger/ folder of the private repository)")
    args = ap.parse_args(argv)
    status = 0
    if args.source:
        if not args.source.is_dir():
            print(f"not a folder: {args.source}", file=sys.stderr)
            return 1
        status = 1 if copy_from(args.source) else 0
    for digest, rel in entries():
        path = HERE / rel
        if not path.exists():
            print(f"MISSING: {rel} (see the module docstring)", file=sys.stderr)
            status = 1
            continue
        got = sha256(path)
        if got != digest:
            print(f"HASH MISMATCH: {rel}: expected {digest}, got {got}", file=sys.stderr)
            status = 1
        else:
            print(f"OK: {rel}")
    return status


if __name__ == "__main__":
    sys.exit(main())
