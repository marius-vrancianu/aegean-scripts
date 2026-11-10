"""Layers L0 and L1 (A1.8). Specification: docs/layers.md.

L0: every token's sign_id (GORILA/Bennett). lineara.xyz and SigLA give it
    directly (A1.7). Younger gives values; this module maps them to sign IDs
    with a cited table, and validates the map against SigLA on shared documents.
L1: one conventional value per L0 sign, assigned UNIFORMLY from the sign ID,
    whatever the source: Unicode Linear B syllable values (Unicode 15.1,
    Linear B Syllabary block, which encodes Bennett number + value). Signs that
    Unicode leaves without a value (*22, *34, *56, *79, *82 ...) and Linear A-only
    signs keep their number ("*79", "*301"), as the plan's L1 definition says.
    Fractions keep their letter names (J, E, L2 ...).

A source's own printed value stays in Token.l1_value; Token.l1 is the uniform
layer. A mismatch between the two is data for A1.9, not corrected here.
"""
from __future__ import annotations

import collections
import difflib
import re
import unicodedata as ud
from dataclasses import replace

from aegean.corpus import schema
from aegean.corpus.schema import FRACTION_IDS, Token, Witness

# --- L1: Unicode Linear B syllable values ----------------------------------------------

LB_VALUES: dict[str, str] = {}
for _o in range(0x10000, 0x10080):
    _m = re.match(r"LINEAR B SYLLABLE B(\d{3}) (.+)$", ud.name(chr(_o), ""))
    if _m:
        LB_VALUES[f"AB{_m.group(1)}"] = _m.group(2)
FRACTION_LETTER = {v: k for k, v in FRACTION_IDS.items() if k != "OMEGA"}


def l1_of(sign_id: str | None) -> str | None:
    """The uniform L1 value of an L0 sign: Unicode Linear B value, fraction letter, or "*number"."""
    if sign_id is None:
        return None
    if sign_id in FRACTION_LETTER:
        return FRACTION_LETTER[sign_id]
    if sign_id in schema.FRACTION_LIGATURES:
        return "".join(FRACTION_LETTER[c] for c in schema.FRACTION_LIGATURES[sign_id])
    if sign_id.startswith("SigLA:"):
        return None
    base = schema.base_id(sign_id)
    if base in LB_VALUES and sign_id == base:
        return LB_VALUES[base]
    m = re.match(r"^(?:AB|A)(\d{3})(.*)$", sign_id)
    return f"*{int(m.group(1))}{m.group(2)}" if m else sign_id


# --- Younger value -> L0 ------------------------------------------------------------------

# Values Younger prints that the Unicode Linear B table does not give, each with its evidence.
YOUNGER_EXTRA = {
    "PA3": ("AB056", "Younger, introduction, 'Phonetic values of the signs': *56=PA3"),
    "PU3": ("A314", "Younger, introduction: *314 = PU3"),
    "ZU": ("AB079", "Younger writes the same HT 13 word KU-*79-NI and KU-ZU-NI (introduction); SigLA HT 13 has AB079 there"),
    "AI": ("AB043", "SigLA sign table: AB43 = ai (Unicode Linear B writes A3)"),
}
YOUNGER_VALUE_MAP: dict[str, tuple[str, str]] = {v: (k, "Unicode Linear B") for k, v in LB_VALUES.items()}
YOUNGER_VALUE_MAP.update(YOUNGER_EXTRA)

# Logogram labels: SigLA's sign-table names (CC BY-NC-SA), e.g. VIN = AB131 with variants a/b/c.
LOGOGRAM_LABELS = {
    "VIN": "AB131", "OVIS": "AB021", "CAP": "AB022", "BOS": "AB023", "FIC": "AB030", "GRA": "AB120",
    "OLIV": "AB122", "AROM": "AB123", "SUS": "AB085", "TELA": "AB054", "VIR": "AB100", "OLE": "A302",
}
_LABEL = re.compile(r"^(" + "|".join(sorted(LOGOGRAM_LABELS, key=len, reverse=True)) + r")([a-z]{0,2})$")
_STAR = re.compile(r"^\*(\d{2,3})(?:VAS)?([a-z]*)$")
_BRACED = re.compile(r"\{\*(\d{3})([a-z]*)\}")


def younger_value_to_l0(value: str) -> tuple[str | None, str]:
    """(sign_id, rule) for one of Younger's printed values; (None, reason) if unmapped."""
    v = value.strip()
    if m := _STAR.match(v):
        return schema.canonical_id("A", m.group(1), m.group(2) or None), "star_number"
    if v in YOUNGER_VALUE_MAP:
        return YOUNGER_VALUE_MAP[v][0], "value_table"
    if v in FRACTION_IDS:
        return FRACTION_IDS[v], "fraction_letter"
    if m := _LABEL.match(v):
        return schema.canonical_id("A", int(LOGOGRAM_LABELS[m.group(1)][-3:]), m.group(2) or None), "logogram_label"
    if len(v) > 1 and v[-1] in "fm" and v[:-1] in YOUNGER_VALUE_MAP:  # QIf = AB021f (sex variants of logograms)
        sid = YOUNGER_VALUE_MAP[v[:-1]][0]
        return schema.canonical_id("A", int(sid[-3:]), v[-1]), "value_table+variant"
    return None, "unmapped"


def younger_logogram_to_l0(cell: str, composites: dict[str, str]) -> tuple[str | None, list[str], str]:
    """(sign_id, components, rule) for a Younger logogram cell.

    Priority: Younger's own brace number ({*574}); a single label or *number;
    a ligature written out ("*301+*311") matched to SigLA's composition text;
    otherwise the components only.
    """
    c = cell.strip().strip("[]").strip()
    if m := _BRACED.search(c):
        return schema.canonical_id("A", m.group(1), m.group(2) or None), [], "brace_number"
    c = re.sub(r"\s*•\s*", "", c).strip("[] ")
    sid, rule = younger_value_to_l0(c)
    if sid:
        return sid, [], rule
    norm = c.replace(" ", "")
    if norm in composites:
        return composites[norm], [], "sigla_composition_text"
    parts = [p for p in re.split(r"\+", c) if p]
    comps = [younger_value_to_l0(p.strip("[] "))[0] for p in parts]
    if len(parts) > 1 and all(comps):
        return None, comps, "components_only"
    return None, [x for x in comps if x], "unmapped"


def sigla_composites(signs) -> dict[str, str]:
    """{composition text without spaces: canonical ID} from SigLA's sign table (e.g. "*301+*311")."""
    out = {}
    for s in signs:
        if s.composition_text:
            out[s.composition_text.replace(" ", "")] = schema.from_sigla_id(s.sign_id)
    return out


# --- applying the layers -----------------------------------------------------------------------

def apply(w: Witness, composites: dict[str, str] | None = None) -> Witness:
    """A copy of `w` with L0 completed (Younger) and the uniform L1 filled for every token."""
    composites = composites or {}
    out = replace(w, lines=[replace(ln, items=[replace(it, tokens=[replace(t) for t in it.tokens])
                                                for it in ln.items]) for ln in w.lines])
    for ln in out.lines:
        for it in ln.items:
            for t in it.tokens:
                if w.source == "younger" and t.sign_id is None and not t.unidentified:
                    if it.kind == "logogram":
                        sid, comps, rule = younger_logogram_to_l0(t.written_as, composites)
                        if comps and not t.components:
                            t.components = comps
                    else:
                        sid, rule = younger_value_to_l0(t.written_as)
                    t.sign_id = sid
                    t.flags.append(f"l0:{rule}")
                t.l1 = l1_of(t.sign_id)
    out.layer = "L0+L1"
    return out


# --- validation against SigLA ------------------------------------------------------------------

def _syllabic_seq(w: Witness) -> list[Token]:
    return [t for ln in w.lines for it in ln.items if it.kind == "word" for t in it.tokens if not t.unidentified]


def validate_against_sigla(pairs: list[tuple[Witness, list[Witness]]]) -> dict:
    """Align Younger's mapped word signs with SigLA's on documents both have.

    pairs: (Younger witness after `apply`, SigLA witnesses of the same document, sides in order).
    Alignment: difflib on base sign IDs; only equal-length 'replace' blocks and 'equal'
    blocks are scored. Returns per-value agreement counts.
    """
    per_value = collections.defaultdict(collections.Counter)
    matched = mismatched = 0
    examples = collections.defaultdict(list)
    for y, sws in pairs:
        ys = _syllabic_seq(y)
        ss = [t for w in sws for t in _syllabic_seq(w)]
        a = [schema.base_id(t.sign_id) or "?" for t in ys]
        b = [schema.base_id(t.sign_id) or "?" for t in ss]
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
            if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    key = ys[i].written_as
                    per_value[key][b[j]] += 1
                    if a[i] == b[j]:
                        matched += 1
                    else:
                        mismatched += 1
                        if len(examples[key]) < 3:
                            examples[key].append((y.source_id, b[j]))
    return {"aligned": matched + mismatched, "agree": matched, "disagree": mismatched,
            "per_value": {k: dict(v) for k, v in per_value.items()}, "examples": dict(examples)}
