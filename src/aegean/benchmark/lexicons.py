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


# ---- English verbs (an unrelated-language lexicon for M1; H-A5-02) ----------------------------

CMUDICT_COMMIT = "74790861f652b15e4ac49015a90074ad62a27690"
CMUDICT_SHA256 = "81917843c7f44ce2b094ac63873c2c7a4cf802040792c455ba3ca406891c3d22"
CMUDICT = REPO / f"data/raw/cmudict/{CMUDICT_COMMIT[:12]}/cmudict.dict"
WORDNET_COMMIT = "550b6625bcef1f2abff2ff770a5a0d272c9c6b2a"
WORDNET_SHA256 = "cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59"
WORDNET_ZIP = REPO / f"data/raw/wordnet/{WORDNET_COMMIT[:12]}/wordnet.zip"
ENGLISH_SIZE = 502  # the number of skeletons in hebrew-strong-verbs

# ARPAbet consonant (and r-coloured vowel) -> M1 class, by the classes HEBREW_CLASS uses:
# P labial stops and fricatives (Hebrew bet/pe are b~v, p~f), K velar stops, T and D as Hebrew tav and dalet
# (including their fricative values th and dh), S every sibilant and affricate (Hebrew zayin, samekh,
# tsade, shin), R liquids, M, N nasals, H the glottal fricative, W, J (y). Vowels are dropped.
ENGLISH_CLASS = {
    "P": "P", "B": "P", "F": "P", "V": "P",
    "K": "K", "G": "K",
    "T": "T", "TH": "T", "D": "D", "DH": "D",
    "S": "S", "Z": "S", "SH": "S", "ZH": "S", "CH": "S", "JH": "S",
    "R": "R", "L": "R", "ER": "R",
    "M": "M", "N": "N", "NG": "N",
    "HH": "H", "W": "W", "Y": "J",
}


def cmudict_first(text: str) -> dict[str, list[str]]:
    """Each word's first pronunciation (the entry without "(2)", "(3)" ...), as ARPAbet phones without stress."""
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith(";;;"):
            continue
        parts = line.split("#", 1)[0].split()
        word, phones = parts[0], parts[1:]
        if "(" in word:
            continue
        out.setdefault(word, [re.sub(r"\d", "", p) for p in phones])
    return out


def english_skeleton(phones: list[str]) -> str:
    return "".join(ENGLISH_CLASS.get(p, "") for p in phones)


def wordnet_verbs(index_verb: str) -> list[tuple[str, int]]:
    """(lemma, tagged sense count) for every single-word, purely alphabetic verb lemma in WordNet's index.verb.

    Line format (WordNet 3.0, wndb(5)): lemma pos synset_cnt p_cnt [ptr_symbol...] sense_cnt tagsense_cnt offsets.
    The tagged sense count is how often the lemma's senses were tagged in the SemCor corpus: a frequency proxy.
    """
    out = []
    for line in index_verb.splitlines():
        if not line or line.startswith(" "):
            continue
        f = line.split()
        lemma, p_cnt = f[0], int(f[3])
        tagsense = int(f[4 + p_cnt + 1])
        if lemma.isalpha() and lemma.isascii():
            out.append((lemma, tagsense))
    return out


def english_verb_skeletons(index_verb: str, cmudict_text: str, size: int = ENGLISH_SIZE,
                           min_len: int = 2, max_len: int = 4) -> tuple[frozenset[str], dict]:
    """The first `size` distinct skeletons of English verbs, most frequent verbs first.

    Verbs are ranked by tagged sense count (descending), ties alphabetically; a verb without a CMUdict entry,
    or whose skeleton is shorter than min_len or longer than max_len, is skipped.
    """
    pron = cmudict_first(cmudict_text)
    ranked = sorted(wordnet_verbs(index_verb), key=lambda x: (-x[1], x[0]))
    forms: list[str] = []
    seen: set[str] = set()
    skipped = {"no_pronunciation": 0, "length": 0, "duplicate": 0}
    last = None
    for lemma, count in ranked:
        if len(forms) == size:
            break
        if lemma not in pron:
            skipped["no_pronunciation"] += 1
            continue
        sk = english_skeleton(pron[lemma])
        if not min_len <= len(sk) <= max_len:
            skipped["length"] += 1
            continue
        if sk in seen:
            skipped["duplicate"] += 1
            continue
        seen.add(sk)
        forms.append(sk)
        last = (lemma, count)
    if len(forms) < size:
        raise ValueError(f"only {len(forms)} distinct skeletons, {size} wanted")
    return frozenset(forms), {"verbs_ranked": len(ranked), "last_verb_taken": last, "skipped": skipped}


def english_verbs(cmudict: Path = CMUDICT, wordnet_zip: Path = WORDNET_ZIP, verify_hash: bool = True) -> Lexicon:
    import zipfile
    for path, want, script in ((cmudict, CMUDICT_SHA256, "cmudict"), (wordnet_zip, WORDNET_SHA256, "wordnet")):
        if not path.exists():
            raise FileNotFoundError(f"{path} is not fetched; run python data/raw/{script}/fetch.py")
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if verify_hash and got != want:
            raise RuntimeError(f"HASH MISMATCH for {path}: {got}, expected {want}")
    with zipfile.ZipFile(wordnet_zip) as z:
        index_verb = z.read("wordnet/index.verb").decode("utf-8")
    forms, info = english_verb_skeletons(index_verb, cmudict.read_text(encoding="utf-8"))
    return Lexicon("english-verbs", forms, "real", {
        "source": "Princeton WordNet 3.0 index.verb (nltk_data) + CMU Pronouncing Dictionary",
        "wordnet_commit": WORDNET_COMMIT, "cmudict_commit": CMUDICT_COMMIT,
        "sha256": hashlib.sha256((WORDNET_SHA256 + CMUDICT_SHA256).encode()).hexdigest(),
        "licence": "WordNet 3.0 licence; CMUdict BSD-style",
        "conversion": "single-word verbs by SemCor tagged-sense count; first CMUdict pronunciation; consonants "
                      "to M1 classes (ENGLISH_CLASS); length 2-4; first 502 distinct skeletons",
        **info})


REGISTRY["english-verbs"] = english_verbs
