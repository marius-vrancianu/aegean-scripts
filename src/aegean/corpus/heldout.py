"""Held-out document list. Every corpus builder must filter through this."""
from pathlib import Path

HELDOUT_FILE = Path(__file__).resolve().parents[3] / "data" / "heldout.txt"


def load_heldout(path: Path = HELDOUT_FILE) -> dict[str, set[str]]:
    """Return {source: {doc_id, ...}} from data/heldout.txt."""
    out: dict[str, set[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        source, doc_id = line.split(":", 1)
        out.setdefault(source, set()).add(doc_id)
    return out


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
