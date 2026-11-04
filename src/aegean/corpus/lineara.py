"""Read the lineara.xyz data file into L0 documents.

Only sign codepoints are used: the `words` field (sign-groups as Unicode
Linear A / Aegean-number codepoints, with '\n' between entry lines).
`transliteratedWords` / `translatedWords` are never read here; they hold L1
values and interpretations (CLAUDE.md, Data rules).

Held-out documents are removed by name before any record is parsed.

Conventions found in this source (snapshot 9c81beba, checked 2026-11-04):
- U+1076B (unassigned in Unicode 15.1) marks a broken edge / lacuna. It is
  dropped from the transliteration and sits at the edge of damaged groups,
  e.g. "[RA-RI" and "2]" on HT 122a. Recorded as damage flags.
- U+10100-10102 are Aegean word separators / check mark.
- The '\n' breaks in `words` follow lineara's entry segmentation, which can
  differ from the physical lines given in its `transcription` field.
"""
from __future__ import annotations

import json
import re
import unicodedata as ud
from dataclasses import asdict, dataclass, field
from pathlib import Path

SOURCE = "lineara.xyz"
LACUNA = "\U0001076b"
_MAP_START = "var inscriptions = new Map(["
_RECORD_RE = re.compile(r'\n\["([^"]+)",(\{.*?\n\})\]', re.S)
_TRAILING_COMMA_RE = re.compile(r",(\s*[\]}])")


@dataclass
class Token:
    type: str  # group | numeral | fraction | separator | lacuna | other | mixed
    raw: str
    signs: list[str] = field(default_factory=list)  # sign IDs, e.g. "AB081"
    value: int | None = None  # numerals: additive integer value of the token
    fractions: list[str] = field(default_factory=list)  # fraction letters, symbolic (J, E, L2, JE...)
    damaged_left: bool = False
    damaged_right: bool = False
    flags: list[str] = field(default_factory=list)


@dataclass
class Document:
    id: str
    source: str
    site: str
    support: str
    scribe: str
    period: str
    findspot: str
    lines: list[list[Token]]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)


def char_class(ch: str) -> tuple[str, str | int | None]:
    """Classify one codepoint. Returns (class, payload)."""
    o = ord(ch)
    name = ud.name(ch, "")
    if ch == LACUNA:
        return "lacuna", None
    if name.startswith("AEGEAN NUMBER"):
        return "numeral", int(ud.numeric(ch))
    if 0x10740 <= o <= 0x10756:  # Linear A fraction signs A701-A732
        return "fraction", name.split()[-1]
    if name.startswith("LINEAR A SIGN"):
        return "sign", name.split()[3]
    if name.startswith("AEGEAN WORD SEPARATOR"):
        return "separator", None
    return "other", f"U+{o:04X}"


def tokenize(raw: str) -> Token:
    classes = [char_class(c) for c in raw]
    kinds = {k for k, _ in classes if k != "lacuna"}
    tok = Token(type="other", raw=raw)
    tok.damaged_left = raw.startswith(LACUNA)
    tok.damaged_right = raw.endswith(LACUNA)
    if LACUNA in raw.strip(LACUNA):
        tok.flags.append("internal_lacuna")
    if not kinds:
        tok.type = "lacuna"
    elif kinds == {"sign"}:
        tok.type = "group"
        tok.signs = [p for k, p in classes if k == "sign"]
    elif kinds == {"numeral"}:
        tok.type = "numeral"
        tok.value = sum(p for k, p in classes if k == "numeral")
    elif kinds == {"fraction"}:
        tok.type = "fraction"
        tok.fractions = [p for k, p in classes if k == "fraction"]
    elif kinds == {"separator"}:
        tok.type = "separator"
    elif len(kinds) == 1:
        tok.type = "other"
        tok.flags += [p for k, p in classes if k == "other"]
    else:
        tok.type = "mixed"
        tok.signs = [p for k, p in classes if k == "sign"]
        tok.fractions = [p for k, p in classes if k == "fraction"]
        nums = [p for k, p in classes if k == "numeral"]
        tok.value = sum(nums) if nums else None
        tok.flags += [p for k, p in classes if k == "other"]
    return tok


def iter_raw_records(path: Path, heldout: set[str]):
    """Yield (doc_id, record dict), skipping held-out IDs before parsing them."""
    text = path.read_text(encoding="utf-8")
    start = text.index(_MAP_START) + len(_MAP_START)
    end = text.index("\n]);", start)
    for doc_id, body in _RECORD_RE.findall(text[start:end]):
        if doc_id in heldout:
            continue
        body = _TRAILING_COMMA_RE.sub(r"\1", body)
        body = re.sub(r"\\u\{([0-9a-fA-F]+)\}", lambda m: chr(int(m.group(1), 16)), body)
        yield doc_id, json.loads(body)


_BRACKET_RE = re.compile(r"\[(?!\?\])|(?<!\[\?)\]")


def to_document(doc_id: str, rec: dict) -> Document:
    words = rec.get("words", [])
    translit = rec.get("transliteratedWords", [])
    # The only thing read from the transliteration is its editorial brackets
    # ("[" / "]" other than "[?]", which marks an unidentified sign element).
    # lineara marks some damage there and not with U+1076B (e.g. HT 104 "TE+RO[").
    aligned = len(translit) == len(words)
    lines: list[list[Token]] = [[]]
    for i, raw in enumerate(words):
        if raw == "\n":
            lines.append([])
            continue
        tok = tokenize(raw)
        if aligned and _BRACKET_RE.search(translit[i]):
            tok.flags.append("translit_bracket")
        lines[-1].append(tok)
    # (All non-held-out records in snapshot 9c81beba are aligned; tests check this.)
    lines = [ln for ln in lines if ln]
    return Document(
        id=doc_id,
        source=SOURCE,
        site=rec.get("site", ""),
        support=rec.get("support", ""),
        scribe=rec.get("scribe", ""),
        period=rec.get("context", ""),
        findspot=rec.get("findspot", ""),
        lines=lines,
    )


def load_documents(path: Path, heldout: set[str]) -> list[Document]:
    return [to_document(i, r) for i, r in iter_raw_records(path, heldout)]
