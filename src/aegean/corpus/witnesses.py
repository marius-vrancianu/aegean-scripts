"""Per-source adapters into the common schema (A1.7): one Witness per source record.

Each adapter maps only what its source records and leaves everything else None
(docs/schema.md, "Field coverage by source"). Nothing is reconciled here.
"""
from __future__ import annotations

import re

from aegean.corpus import lineara, schema, sigla, younger
from aegean.corpus.schema import FRACTION_IDS, FRACTION_LIGATURES, LIGATURE_LETTERS, Item, Line, Token, Witness

VERSIONS = {"lineara.xyz": "9c81beba669a", "sigla": "0c4ef69f5de4", "younger": "05305bc5235d"}


def _fraction_token(letters: str, written_as: str | None = None) -> Token:
    """A fraction sign by its letter name; ligature letters (JE, DD ...) keep their components."""
    if letters in LIGATURE_LETTERS:
        sid = LIGATURE_LETTERS[letters]
        return Token(written_as or letters, sid, "fraction", list(FRACTION_LIGATURES[sid]))
    sid = FRACTION_IDS.get(letters)
    t = Token(written_as or letters, sid, "fraction")
    if sid is None:
        t.flags.append("unknown_fraction_letter")
    return t


# --- lineara.xyz ------------------------------------------------------------------

def from_lineara(d: lineara.Document) -> Witness:
    """lineara.xyz: L0 from Unicode codepoints (never from transliteratedWords/translatedWords).

    Lines are lineara.xyz's entry lines (ref_kind "entry"), not physical lines.
    Breaks are recorded only where lineara marks a lacuna (U+1076B) at a group
    edge, or where its transliteration has an editorial bracket; an unmarked
    edge is None, not "", because lineara's damage marking is incomplete.
    """
    w = Witness("lineara.xyz", d.id, VERSIONS["lineara.xyz"], None, "L0", period=d.period or None,
                scribe=d.scribe or None)
    for li, toks in enumerate(d.lines):
        line = Line(li, None, "entry")
        for t in toks:
            it = Item("other", raw=t.raw, flags=list(t.flags))
            if t.damaged_left:
                it.left_break = "]"
            if t.damaged_right:
                it.right_break = "["
            if t.type in ("group", "mixed"):
                it.kind = "word" if t.type == "group" else "mixed"
                it.tokens = [Token(s, schema.from_unicode_name("LINEAR A SIGN " + s)) for s in t.signs]
                if t.type == "mixed":
                    it.tokens += [_fraction_token(f) for f in t.fractions]
                    it.numeral_value = t.value
            elif t.type == "numeral":
                it.kind, it.numeral_value = "numeral", t.value
            elif t.type == "fraction":
                it.kind = "fraction"
                it.tokens = [_fraction_token(f) for f in t.fractions]
            elif t.type == "separator":
                it.kind = "divider"
                if line.items:
                    line.items[-1].divider_after = True
            elif t.type == "lacuna":
                it.kind = "lacuna"
            elif t.type == "other" and t.raw.strip() == "—":
                it.kind = "ruling"  # lineara.xyz convention, checked on GORILA facsimiles (DATA_SOURCES)
            line.items.append(it)
        w.lines.append(line)
    return w


# --- SigLA ---------------------------------------------------------------------------

SIGLA_CLASS_ITEM = {"logogram": "logogram", "fraction": "fraction", "transaction": "transaction",
                    "unknown": "unknown", "punctuation": "punctuation"}
SIGLA_EDGE = {0: ("", ""), 1: ("]-", "-["), 2: ("]", "[")}


def _components(comp) -> list[str]:
    if comp is None:
        return []
    if isinstance(comp, str):
        return [schema.from_sigla_id(comp)]
    if isinstance(comp, dict) and "parts" in comp:
        return [c for p in comp["parts"] for c in _components(p)]
    return []  # an unidentified component


def from_sigla(d: sigla.Document, signs: dict[str, sigla.Sign]) -> Witness:
    """SigLA: L0 sign IDs from the database, per-sign sure/unsure, erasure, word edges.

    SigLA records no lines (one line, ref_kind "none"), no numeral values and no
    restorations. Word-edge codes are mapped to "]" / "]-" as the site renders them
    and kept raw in the item flags.
    """
    w = Witness("sigla", d.id, VERSIONS["sigla"], None, "L0", period=d.period)
    line = Line(0, None, "none")
    words = {wd.index: wd for wd in d.words}
    placed: set[int] = set()
    for a in d.attestations:
        tok = _sigla_token(a, signs)
        if a.word is not None:
            if a.word in placed:
                continue
            placed.add(a.word)
            wd = words[a.word]
            left, right = SIGLA_EDGE.get(wd.left_edge, ("?", "?"))[0], SIGLA_EDGE.get(wd.right_edge, ("?", "?"))[1]
            it = Item("word", [_sigla_token(d.attestations[i], signs) for i in wd.attestations],
                      left_break=left, right_break=right,
                      flags=[f"edge_left={wd.left_edge}", f"edge_right={wd.right_edge}"])
        else:
            it = Item(SIGLA_CLASS_ITEM.get(a.sign_class, "other"), [tok])
        line.items.append(it)
    w.lines.append(line)
    if any(a.hidden for a in d.attestations):
        w.flags.append("has_hidden_attestations")
    if d.metadata_id:
        w.flags.append(f"metadata_id={d.metadata_id}")
    return w


def _sigla_token(a: sigla.Attestation, signs: dict[str, sigla.Sign]) -> Token:
    role = {"syllabogram": "syllabogram", "logogram": "logogram", "fraction": "fraction",
            "transaction": "transaction", "punctuation": "punctuation"}.get(a.sign_class, "unknown")
    if a.sign_id is None:
        t = Token(f"[{a.sign_status}]", None, role, unidentified=True)
    else:
        sid = schema.from_sigla_id(a.sign_id)
        comps = list(FRACTION_LIGATURES.get(sid, ())) or _components(signs[a.sign_id].composition if a.sign_id in signs else None)
        t = Token(a.sign_id, sid, role, comps, doubtful=not a.reading_sure)
    t.erased = a.erased
    t.bbox = a.bbox
    if a.hidden:
        t.flags.append("hidden")
    if a.class_uncertain:
        t.flags.append("class_uncertain")
    return t


# --- Younger -----------------------------------------------------------------------------

_STAR = re.compile(r"^\*(\d{2,3})([a-z]*)$")


def _younger_sign(s: younger.Sign) -> Token:
    """Younger gives values (L1). A "*nnn" value is a sign number and maps to L0 directly;
    other values wait for the A1.8 value table (sign_id None)."""
    if s.unidentified:
        t = Token("•", None, None, unidentified=True)
    else:
        m = _STAR.match(s.value)
        sid = schema.canonical_id("AB" if int(m.group(1)) < 300 else "A", m.group(1), m.group(2) or None) if m else None
        t = Token(s.value, sid, None, l1_value=None if m else s.value)
    t.doubtful, t.erased, t.restored, t.conjectural = s.doubtful, s.erased, s.restored, s.conjectural
    t.break_before, t.break_after = s.break_before, s.break_after
    return t


def _number_item(raw: str, doubtful: bool) -> Item:
    digits = re.findall(r"\d+", raw)
    it = Item("numeral", raw=raw, numeral_value=sum(int(x) for x in digits) if digits else None)
    if not digits:
        it.flags.append("unparsed_number")
    if raw.lstrip().startswith("]"):
        it.left_break = "]"
    if "[" in raw:
        it.right_break = "["
    if doubtful:
        it.flags.append("doubtful")
    return it


def _fraction_items(raw: str, doubtful: bool) -> Item:
    it = Item("fraction", raw=raw)
    for part in raw.split():
        letters = part.strip("[]")
        if part.startswith("]"):
            it.left_break = "]"
        if part.endswith("["):
            it.right_break = "["
        if letters in ("•", "[•]") or part == "[•]":
            it.tokens.append(Token(part, None, "fraction", unidentified=True))
        elif letters.startswith("vest"):
            it.flags.append("vestigia")  # traces only
        elif letters:
            tok = _fraction_token(letters, part)
            tok.doubtful = doubtful
            it.tokens.append(tok)  # an unrecognised letter keeps flag unknown_fraction_letter
    return it


_BRACED = re.compile(r"\{\*(\d{3})([a-z]*)\}")


def from_younger(d: younger.Document) -> Witness:
    """Younger 2024: physical side.line refs, per-sign doubt/erasure/restoration/conjecture.

    Commentary rows (Younger's reconstructions, e.g. PH 31) are never included.
    Statement signs are L1 values except "*nnn"; logograms keep their printed
    form, with the sign number from Younger's braces ("OVIS+SI {*512}") as L0.
    """
    scribe = next((a for a in d.annotations if "Scribe" in a), None)
    w = Witness("younger", d.id, VERSIONS["younger"], None, "L0+L1", scribe=scribe,
                notes=list(d.notes), flags=list(d.flags))
    if d.commentary_rows:
        w.flags.append(f"commentary_rows_omitted={len(d.commentary_rows)}")
    for li, r in enumerate(d.rows):
        line = Line(li, r.ref, "physical" if r.ref else "none")
        for g in r.statement:
            if g.lacuna_dots:
                line.items.append(Item("lacuna", raw=g.raw, lacuna_estimate=g.lacuna_dots))
                continue
            it = Item("word", [_younger_sign(s) for s in g.signs], divider_after=g.divider_after, raw=g.raw)
            if not g.signs:
                it.kind = "divider" if "•" in g.raw else "other"
                if g.doubtful:
                    it.flags.append("doubtful")
            line.items.append(it)
        if r.logogram:
            m = _BRACED.search(r.logogram)
            sid = schema.canonical_id("A", m.group(1), m.group(2) or None) if m else None
            tok = Token(r.logogram, sid, "logogram", doubtful=r.logogram_doubtful)
            if not m:
                tok.l1_value = r.logogram  # a logogram label (OVIS, *303+D ...): mapped in A1.8
                st = _STAR.match(r.logogram.strip("[]"))
                if st:
                    tok.sign_id = schema.canonical_id("AB" if int(st.group(1)) < 300 else "A", st.group(1),
                                                      st.group(2) or None)
                    tok.l1_value = None
            line.items.append(Item("logogram", [tok], raw=r.logogram))
        if r.number:
            line.items.append(_number_item(r.number, r.number_doubtful))
        if r.fraction:
            line.items.append(_fraction_items(r.fraction, r.fraction_doubtful))
        for o in r.other:
            kind = "ruling" if o.startswith(("_", "—")) else ("vacat" if o.lower().startswith(("vacat", "vacant", "deest")) else "other")
            line.items.append(Item(kind, raw=o))
        for k, v in r.extra.items():
            line.items.append(Item("other", raw=f"{k}: {v}", flags=[k]))
        w.lines.append(line)
    return w
