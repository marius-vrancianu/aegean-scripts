"""Reproduce Finding 001 with the original, unmodified scripts.

The original scripts hard-code ~/yadiktu/ as their data folder. Rather than edit
them, this wrapper builds a temporary HOME containing yadiktu/{la.js,
HebrewStrong.xml, src/*.py} and runs them there.

  python experiments/finding-001/reproduce.py             # original run (all documents)
  python experiments/finding-001/reproduce.py --exclude-heldout

--exclude-heldout drops the records listed in data/heldout.txt from la.js
before running. The records are removed by name; their text is never printed.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))
from aegean.corpus.heldout import load_heldout  # noqa: E402

LINEARA = REPO / "data/raw/lineara.xyz/9c81beba669a/LinearAInscriptions.js"
HEB_COMMIT = "21c9add13bc727d3a951361778e97e3ff7afd1ce"
HEB_URL = f"https://raw.githubusercontent.com/openscriptures/HebrewLexicon/{HEB_COMMIT}/HebrewStrong.xml"
HEB_CACHE = REPO / f"data/raw/openscriptures-HebrewLexicon/{HEB_COMMIT[:12]}/HebrewStrong.xml"


def ensure_inputs() -> None:
    if not LINEARA.exists():
        subprocess.run([sys.executable, str(REPO / "data/raw/lineara.xyz/fetch.py")], check=True)
    if not HEB_CACHE.exists():
        HEB_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(HEB_URL, timeout=120) as r:
            HEB_CACHE.write_bytes(r.read())
    print("HebrewStrong.xml sha256", hashlib.sha256(HEB_CACHE.read_bytes()).hexdigest())


def strip_records(text: str, ids: set[str]) -> tuple[str, int]:
    """Remove top-level records ["ID",{...}] for the given IDs."""
    removed = 0
    for doc_id in ids:
        start = text.find(f'["{doc_id}",{{')
        if start < 0:
            continue
        nxt = text.find('\n["', start + 1)
        end = nxt + 1 if nxt >= 0 else len(text)
        text = text[:start] + text[end:]
        removed += 1
    return text, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude-heldout", action="store_true")
    args = ap.parse_args()
    ensure_inputs()
    with tempfile.TemporaryDirectory() as home:
        y = Path(home) / "yadiktu"
        (y / "src").mkdir(parents=True)
        for f in ("nulltest.py", "run.py", "run2.py"):
            shutil.copy(HERE / "original" / f, y / "src" / f)
        shutil.copy(HEB_CACHE, y / "HebrewStrong.xml")
        js = LINEARA.read_text(encoding="utf-8")
        if args.exclude_heldout:
            ids = load_heldout().get("lineara.xyz", set())
            js, n = strip_records(js, ids)
            print(f"excluded {n} held-out record(s); remaining check:",
                  "clean" if not any(f'["{i}",' in js for i in ids) else "FAILED")
        (y / "la.js").write_text(js, encoding="utf-8")
        env = dict(os.environ, HOME=home)
        for script in ("nulltest.py", "run.py", "run2.py"):
            print(f"\n===== {script} =====", flush=True)
            subprocess.run([sys.executable, "-I", str(y / "src" / script)], cwd=home, env=env, check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
