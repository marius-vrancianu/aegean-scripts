"""Read the SigLA database (sigla.phis.me/database.js) into named records.

SigLA (Salgarella & Castellan; CC BY-NC-SA 4.0, see DATA_SOURCES.md) is a
static site whose OCaml/js_of_ocaml front end loads `database.js`. That file
defines two JavaScript variables, `signs` and `data`. Each holds an OCaml
string literal (inside a single-quoted JS string) whose bytes are an OCaml
`Marshal` value. `load_raw` undoes the two layers of quoting and unmarshals;
`load_documents` / `load_signs` turn the value graph into named records.

SigLA does not document its record layout. Every field mapping below was
checked against the rendered site on 2026-11-10, unless marked otherwise.
Evidence for each mapping is in data/raw/sigla/README.md and the fixture
tests. Fields whose meaning is not established are kept under raw names
(`pos_f2`, `hidden`, `seal_raw`) rather than guessed.

What this module does NOT do:
- no conventional (Linear B) values enter attestations: they are L1 and stay
  in the sign table as `conventional_values` (CLAUDE.md data rules);
- no reconciliation with other sources (A1.6, A1.9);
- no canonical schema (A1.7). These records are a faithful source layer.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from aegean.corpus import ocaml_marshal as om
from aegean.corpus.heldout import load_heldout
from aegean.corpus.ocaml_marshal import Block

SOURCE = "sigla"
_VAR_RE = re.compile(r"var\s+(\w+)\s*=\s*'")

# Standalone attestation classes (position.location = (class, uncertain)).
# Checked against the "role" label on rendered sign pages: HT 13 #5 (0),
# #9 (1), #6 (2); HT 101 #12 (3); HT 101 #13 (4).
STANDALONE_CLASS = {0: "logogram", 1: "fraction", 2: "transaction", 3: "unknown", 4: "punctuation"}
# Attestation sign given as a constant instead of a sign record:
# 0 renders as "[?]" (ARKH 1a #14), 1 as "[unclassified]" (HT 28b #27).
SIGN_CONSTANT = {0: "unidentified", 1: "unclassified"}
# Composition operators (sign-table field 9), matched with the GORILA-style
# text in field 8: 1 "a + b" (ligature), 2 "a | b", 3 "a || b",
# 4 "a+{b}" (binary; b written inside or onto a). Tag 0 is a component leaf.
COMPOSITION_OP = {1: "+", 2: "|", 3: "||", 4: "+{}"}
# Word edge codes, as the word view renders them: 0 intact,
# 1 "]-x" / "x-[", 2 "]x" / "x[" (ARKH 3a w1, ARKH 2 w6, ARKH 1a w1/w5).
EDGE_RENDERING = {0: ("", ""), 1: ("]-", "-["), 2: ("]", "[")}


# --- quoting layers ----------------------------------------------------------

def _js_single_quoted(text: str, start: int) -> tuple[str, int]:
    """Value of the JS single-quoted string whose opening quote is at text[start-1]."""
    out, i = [], start
    js_simple = {"\\": "\\", "'": "'", '"': '"', "n": "\n", "t": "\t", "r": "\r", "0": "\0"}
    while True:
        c = text[i]
        if c == "'":
            return "".join(out), i + 1
        if c == "\\":
            nxt = text[i + 1]
            if nxt in js_simple:
                out.append(js_simple[nxt])
                i += 2
            elif nxt == "u":
                out.append(chr(int(text[i + 2:i + 6], 16)))
                i += 6
            elif nxt == "x":
                out.append(chr(int(text[i + 2:i + 4], 16)))
                i += 4
            else:
                raise ValueError(f"unsupported JS escape \\{nxt} at {i}")
        else:
            out.append(c)
            i += 1


def extract_variables(text: str) -> dict[str, bytes]:
    """{variable name: marshalled bytes} for every `var x = '"..."'` in database.js."""
    out: dict[str, bytes] = {}
    for m in _VAR_RE.finditer(text):
        js_value, _ = _js_single_quoted(text, m.end())
        if not (js_value.startswith('"') and js_value.endswith('"')):
            raise ValueError(f"variable {m.group(1)} does not hold an OCaml string literal")
        out[m.group(1)] = om.unescape_ocaml_literal(js_value[1:-1])
    return out


def load_raw(path: Path) -> dict[str, object]:
    """{variable name: decoded OCaml value}. Raises on any decoding inconsistency."""
    blobs = extract_variables(path.read_text(encoding="utf-8"))
    out = {}
    for name, blob in blobs.items():
        value, used = om.loads_with_size(blob)
        if used != len(blob):
            raise om.MarshalError(f"{name}: {len(blob) - used} trailing bytes after the marshalled value")
        out[name] = value
    return out


# --- records -----------------------------------------------------------------

@dataclass
class Sign:
    sign_id: str  # series + number + variant, e.g. "AB77", "A506bis", "AAF709-2"
    series: str  # A, AB, AAF (fractions), AAP (abstract/punctuation), AAZ (composites)
    number: int
    variant: str | None
    name: str | None  # logogram / fraction name: OVIS, VIN, J, DD, num, SUS+SI
    reference: str | None  # SigLA's reference attestation, e.g. "PH 31a/17"
    composition_text: str | None  # GORILA-style, e.g. "*01 || *02"
    composition: dict | None  # {"op": "+", "parts": [...]} ; leaves are sign IDs
    conventional_values: list[str] = field(default_factory=list)  # L1 (Linear B homomorphs); never L0


@dataclass
class Attestation:
    index: int  # SigLA's attestation index within the document (0-based; the site shows #index+1)
    sign_id: str | None  # None when the sign is unidentified / unclassified
    sign_status: str  # identified | unidentified ("[?]") | unclassified
    reading_sure: bool | None  # sure-reading / unsure-reading on the site; None if no sign
    sign_class: str  # syllabogram (in a word) | logogram | fraction | transaction | unknown | punctuation
    class_uncertain: bool  # the site shows the class with "?"
    word: int | None  # word index (in-word attestations only)
    index_in_word: int | None
    erased: bool  # shown as "Erasure" on the site
    hidden: bool  # raw flag; such attestations are counted but not drawn (HT 22 #3). Meaning unknown.
    pos_f2: int  # raw; always 0 in snapshot 0c4ef69f
    bbox: tuple[int, int, int, int]  # x, y, w, h in drawing pixels


@dataclass
class Word:
    index: int
    attestations: list[int]  # attestation indices, in SigLA's order
    left_edge: int  # 0 intact, 1 / 2 broken (see EDGE_RENDERING); raw code kept
    right_edge: int


@dataclass
class Document:
    id: str
    source: str
    support: str  # SigLA's "kind" (Tablet, Nodule, Roundel ...), spelling as given
    site: str
    dimensions_cm: tuple[float, float, float] | None
    period: str | None
    corpus_link: str | None
    seal_cms: str | None
    seal_motif: str | None
    seal_raw: int | None  # first field of the seal record; meaning unknown
    metadata_id: str | None  # the ID written in the metadata record, only when it differs from the key
    drawing_size: tuple[int, int]
    attestations: list[Attestation]
    words: list[Word]

    def to_dict(self) -> dict:
        return asdict(self)


# --- decoding helpers --------------------------------------------------------

def _s(v) -> str:
    if not isinstance(v, bytes):
        raise om.MarshalError(f"expected a string, got {v!r}")
    return v.decode("utf-8")


def _opt_s(v) -> str | None:
    x = om.option(v)
    return None if x is None else _s(x)


def walk_map(m) -> list[tuple[object, object]]:
    """In-order (key, value) pairs of an OCaml `Map` (AVL nodes [l, k, v, r, h])."""
    out, stack, node = [], [], m
    while stack or isinstance(node, Block):
        while isinstance(node, Block):
            if len(node.fields) != 5:
                raise om.MarshalError(f"not a Map node: {node!r}")
            stack.append(node)
            node = node.fields[0]
        node = stack.pop()
        out.append((node.fields[1], node.fields[2]))
        node = node.fields[3]
    if not om.is_none(node):
        raise om.MarshalError("malformed Map")
    return out


def sign_id_of(rec: Block) -> str:
    series, number, variant = _s(rec.fields[0]), rec.fields[1], _opt_s(rec.fields[5])
    if variant is None:
        return f"{series}{number}"
    sep = "-" if variant[:1].isdigit() else ""
    return f"{series}{number}{sep}{variant}"


def _component(v):
    """A composition component: a sign ID, None for "[?]"-style constants, or a nested node."""
    if isinstance(v, int):
        return None
    if not isinstance(v, Block):
        raise om.MarshalError(f"bad composition component {v!r}")
    if v.tag == 0:  # leaf: (sign record, sure flag) or constant
        s = v.fields[0]
        if isinstance(s, int):
            return {"unidentified": SIGN_CONSTANT.get(s, f"const{s}")}
        return sign_id_of(s.fields[0])
    op = COMPOSITION_OP.get(v.tag)
    if op is None:
        raise om.MarshalError(f"unknown composition operator tag {v.tag}")
    parts = om.to_list(v.fields[0]) if v.tag in (1, 2, 3) else list(v.fields)
    return {"op": op, "parts": [_component(p) for p in parts]}


def to_sign(rec: Block) -> Sign:
    f = rec.fields
    comp = om.option(f[9])
    return Sign(
        sign_id=sign_id_of(rec),
        series=_s(f[0]),
        number=f[1],
        variant=_opt_s(f[5]),
        name=_opt_s(f[4]),
        reference=_opt_s(f[3]),
        composition_text=(_opt_s(f[8]) or "").strip() or None,
        composition=None if comp is None else _component(comp.fields[0]),
        conventional_values=_values(f[2]),
    )


def _values(v) -> list[str]:
    """Sign-table field 2: option of (value, alternative value option), e.g. Some ("da", None)."""
    pair = om.option(v)
    if pair is None:
        return []
    first, alt = pair.fields
    alt = om.option(alt)
    return [_s(first)] + ([] if alt is None else [_s(alt)])


def to_attestation(a: Block) -> Attestation:
    idx, _doc, pos, sign, hidden, bbox = a.fields
    loc, erased, pos_f2 = pos.fields
    where, class_uncertain = loc.fields
    if isinstance(where, Block):
        index_in_word, word = where.fields
        sign_class = "syllabogram"
    else:
        index_in_word = word = None
        sign_class = STANDALONE_CLASS.get(where, f"class{where}")
    if isinstance(sign, int):
        sign_id, status, sure = None, SIGN_CONSTANT.get(sign, f"const{sign}"), None
    else:
        rec, flag = sign.fields
        sign_id, status, sure = sign_id_of(rec), "identified", bool(flag)
    return Attestation(
        index=idx, sign_id=sign_id, sign_status=status, reading_sure=sure,
        sign_class=sign_class, class_uncertain=bool(class_uncertain),
        word=word, index_in_word=index_in_word, erased=bool(erased),
        hidden=bool(hidden), pos_f2=pos_f2, bbox=tuple(bbox.fields),
    )


def to_word(w: Block) -> Word:
    idx, _doc, edges, atts = w.fields
    return Word(index=idx, attestations=[x.fields[0] for x in om.to_list(atts)],
                left_edge=edges.fields[0], right_edge=edges.fields[1])


def to_document(doc_id: str, d: Block) -> Document:
    meta, name, size, atts, words = d.fields
    m = meta.fields
    if _s(name) != doc_id:
        raise om.MarshalError(f"{doc_id}: document name differs from its key")
    # The metadata record's own ID differs from the key in 7 documents of
    # snapshot 0c4ef69f (e.g. KH 87 -> "KH 97"). Kept for A1.9, not resolved here.
    meta_id = _s(m[1])
    dims = om.option(m[6])
    seal = om.option(m[9])
    return Document(
        id=doc_id, source=SOURCE, support=_s(m[0]), site=_s(m[2]),
        dimensions_cm=None if dims is None else tuple(float(x) for x in dims.fields),
        period=_opt_s(m[7]), corpus_link=_opt_s(m[8]),
        seal_cms=None if seal is None else _opt_s(seal.fields[1]),
        seal_motif=None if seal is None else _opt_s(seal.fields[2]),
        seal_raw=None if seal is None else seal.fields[0],
        metadata_id=None if meta_id == doc_id else meta_id,
        drawing_size=tuple(size.fields),
        attestations=[to_attestation(a) for a in atts.fields],
        words=[to_word(w) for w in words.fields],
    )


# --- held-out filter -----------------------------------------------------------

def _norm(doc_id: str) -> str:
    return re.sub(r"\s+", "", doc_id).upper()


def heldout_keys(heldout: dict[str, set[str]] | None = None) -> set[str]:
    """Normalised sigla of every held-out document, from every source in data/heldout.txt.

    SigLA writes sigla with spaces ("HT 13"); lineara.xyz without ("HT13", sides
    as "a"/"b"). Matching on the normalised siglum, with a trailing side letter
    removed, means a SigLA record of a held-out document is excluded even before
    a `sigla:` line exists in data/heldout.txt.
    """
    heldout = load_heldout() if heldout is None else heldout
    keys = set()
    for ids in heldout.values():
        for i in ids:
            n = _norm(i)
            keys.add(n)
            keys.add(re.sub(r"[A-Z]$", "", n) if re.search(r"\d[A-Z]$", n) else n)
    return keys


def is_heldout(doc_id: str, keys: set[str]) -> bool:
    n = _norm(doc_id)
    base = re.sub(r"[A-Z]$", "", n) if re.search(r"\d[A-Z]$", n) else n
    return n in keys or base in keys


# --- entry points ----------------------------------------------------------------

def load_signs(path: Path) -> list[Sign]:
    """Distinct sign records (the site's Map holds each named sign under two keys)."""
    raw = load_raw(path)
    seen, out = set(), []
    for _k, rec in walk_map(raw["signs"]):
        s = to_sign(rec)
        if s.sign_id not in seen:
            seen.add(s.sign_id)
            out.append(s)
    return out


def load_documents(path: Path, heldout: dict[str, set[str]] | None = None) -> list[Document]:
    """All non-held-out documents. Held-out IDs are dropped before their records are interpreted."""
    keys = heldout_keys(heldout)
    raw = load_raw(path)
    out = []
    for k, d in walk_map(raw["data"].fields[0]):
        doc_id = _s(k)
        if is_heldout(doc_id, keys):
            continue
        out.append(to_document(doc_id, d))
    return out
