"""Held-out documents (data/heldout.txt). Two kinds, both listed in that file:

- **Excluded at ingest** (`<source>:<id>` lines; the Knossos sceptre): every
  corpus builder drops these before parsing, so they are in no corpus file.
- **The frozen split** (`split:<document key>` lines; A1.12): these documents
  are in the corpus files, and `aegean.corpus.load` withholds them unless the
  caller names a frozen confirmatory hypothesis.
"""
from pathlib import Path

HELDOUT_FILE = Path(__file__).resolve().parents[3] / "data" / "heldout.txt"
SPLIT_SOURCE = "split"


def _entries(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        source, doc_id = line.split(":", 1)
        yield source, doc_id


def load_heldout(path: Path = HELDOUT_FILE) -> dict[str, set[str]]:
    """Return {source: {doc_id, ...}} for the documents excluded at ingest (not the split)."""
    out: dict[str, set[str]] = {}
    for source, doc_id in _entries(path):
        if source != SPLIT_SOURCE:
            out.setdefault(source, set()).add(doc_id)
    return out


def load_split(path: Path = HELDOUT_FILE) -> set[str]:
    """Canonical document keys of the frozen held-out split (empty before the freeze)."""
    return {doc_id for source, doc_id in _entries(path) if source == SPLIT_SOURCE}


def is_heldout(source: str, doc_id: str, heldout: dict[str, set[str]] | None = None) -> bool:
    heldout = load_heldout() if heldout is None else heldout
    return doc_id in heldout.get(source, set())


# --- cross-source siglum matching ---------------------------------------------
# Sources write sigla differently: SigLA and Younger "HT 13", lineara.xyz "HT13"
# with sides as "a"/"b". Matching on the normalised siglum, with a trailing side
# letter removed, excludes a held-out document from every source even before a
# source-specific line exists in data/heldout.txt. Deliberately over-inclusive.
import re as _re


def _norm(doc_id: str) -> str:
    return _re.sub(r"\s+", "", doc_id).upper()


def _base(n: str) -> str:
    return _re.sub(r"[A-Z]$", "", n) if _re.search(r"\d[A-Z]$", n) else n


def heldout_keys(heldout: dict[str, set[str]] | None = None) -> set[str]:
    """Normalised sigla (with and without side letter) of every held-out document, all sources."""
    heldout = load_heldout() if heldout is None else heldout
    keys = set()
    for ids in heldout.values():
        for i in ids:
            n = _norm(i)
            keys |= {n, _base(n)}
    return keys


def is_heldout_siglum(doc_id: str, keys: set[str]) -> bool:
    n = _norm(doc_id)
    return n in keys or _base(n) in keys
