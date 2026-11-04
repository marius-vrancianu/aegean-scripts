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
