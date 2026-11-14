"""Real lexicons, converted to the forms a method compares against.

Each loader records its source, version and conversion in `Lexicon.meta`.
How a dictionary becomes comparison forms is part of the claim under test:
a different conversion is a different lexicon and gets a different name.

Lexicons so far
- `hebrew-strong-verbs`: verb lemmas of Strong's Hebrew dictionary
  (openscriptures HebrewLexicon, CC BY 4.0; DATA_SOURCES.md), as consonant-class
  skeletons for M1. This is the Finding 001 lexicon.
- a plain file of forms, one per line (`from_file`), for third-party claims.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from aegean.benchmark.interface import Lexicon

REPO = Path(__file__).resolve().parents[3]
HEBREW_COMMIT = "21c9add13bc727d3a951361778e97e3ff7afd1ce"
HEBREW_SHA256 = "a628f4f89f8bdaf2483fd3faf1abc8653cc6717758dfc9f24beb7571d9bdd0c4"
HEBREW_XML = REPO / f"data/raw/openscriptures-HebrewLexicon/{HEBREW_COMMIT[:12]}/HebrewStrong.xml"

# Hebrew letter -> M1 consonant class (final forms included). From Finding 001's nulltest.py.
HEBREW_CLASS = {
    "א": "H", "ה": "H", "ח": "H", "ע": "H",
    "ב": "P", "פ": "P", "ף": "P",
    "ג": "K", "כ": "K", "ך": "K", "ק": "K",
    "ד": "D", "ט": "T", "ת": "T",
    "צ": "S", "ץ": "S", "ז": "S", "ס": "S", "ש": "S",
    "ל": "R", "ר": "R",
    "מ": "M", "ם": "M", "נ": "N", "ן": "N",
    "ו": "W", "י": "J",
}
_VERB = re.compile(r'<w pos="v"[^>]*xml:lang="(heb|arc)">([^<]+)</w>')
_POINTS = re.compile(r"[֑-ׇ]")  # cantillation marks and vowel points


def hebrew_verb_skeletons(xml: str, min_len: int = 2, max_len: int = 4) -> frozenset[str]:
    """Consonant-class skeletons of the verb lemmas (Hebrew and Biblical Aramaic) in HebrewStrong.xml."""
    out = set()
    for m in _VERB.finditer(xml):
        word = _POINTS.sub("", m.group(2))
        sk = "".join(HEBREW_CLASS.get(c, "") for c in word)
        if min_len <= len(sk) <= max_len:
            out.add(sk)
    return frozenset(out)


def hebrew_strong_verbs(path: Path = HEBREW_XML, verify_hash: bool = True) -> Lexicon:
    if not path.exists():
        raise FileNotFoundError(f"{path} is not fetched; run python data/raw/openscriptures-HebrewLexicon/fetch.py")
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if verify_hash and got != HEBREW_SHA256:
        raise RuntimeError(f"HASH MISMATCH for {path}: {got}, expected {HEBREW_SHA256}")
    return Lexicon("hebrew-strong-verbs", hebrew_verb_skeletons(data.decode("utf-8")), "real",
                   {"source": "openscriptures/HebrewLexicon HebrewStrong.xml", "commit": HEBREW_COMMIT,
                    "sha256": got, "licence": "CC BY 4.0",
                    "conversion": "verb lemmas (heb, arc); points removed; letters to M1 classes; length 2-4"})


def from_file(path: Path, name: str | None = None) -> Lexicon:
    """A lexicon from a text file: one form per line; blank lines and lines starting with # are skipped."""
    path = Path(path)
    data = path.read_bytes()
    forms = frozenset(l.strip().upper() for l in data.decode("utf-8").splitlines()
                      if l.strip() and not l.lstrip().startswith("#"))
    return Lexicon(name or path.stem, forms, "real", {"source": str(path), "sha256": hashlib.sha256(data).hexdigest()})


REGISTRY = {"hebrew-strong-verbs": hebrew_strong_verbs}
