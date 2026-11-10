"""Common corpus schema and per-source adapters (A1.7). Specification: docs/schema.md.

Document -> Witness (one source's reading of one document side) -> Line -> Item -> Token.

Conventions that every adapter follows:
- **None vs False.** A mark that a source does not record is None, never False.
  False means the source records that the mark is absent. Example: lineara.xyz
  records no per-sign doubt, so Token.doubtful is None for every lineara token.
- **Provenance.** Every mark belongs to the witness it is in, and a witness has
  exactly one source. Cross-source comparison (A1.9) never merges marks.
- **Layers.** Token.sign_id is L0 (GORILA/Bennett sign number). Token.l1_value
  holds a conventional value only where the source itself gives one (Younger)
  and is never used to fill sign_id here; that mapping is A1.8.
- **Order.** Items and tokens keep the source's linear order. Where a source
  linearises stacked signs, the order is the source's, not the tablet's.
"""
from __future__ import annotations

import re
import unicodedata as ud
from dataclasses import asdict, dataclass, field

SCHEMA_VERSION = "0.2"  # 0.2 (A1.8): Token.l1

# --- canonical sign IDs -------------------------------------------------------

# Fraction signs: GORILA A701-A718 with their letter names (Corazza et al. 2021 use the letters).
FRACTION_IDS = {
    "A": "A701", "B": "A702", "D": "A703", "E": "A704", "F": "A705", "H": "A706", "J": "A707",
    "K": "A708", "L": "A709", "L2": "A709-2", "L3": "A709-3", "L4": "A709-4", "L6": "A709-6",
    "W": "A710", "X": "A711", "Y": "A712", "Ω": "A713", "OMEGA": "A713",
}
# Single signs that encode a combination of fractions (ligatures), with their components in
# the order the sign name gives them. Unicode encodes A714-A717, A726 and A732; SigLA also has
# DDDD (AAF718), which Unicode lacks.
FRACTION_LIGATURES = {
    "A714": ("A701", "A702", "A702"),  # ABB
    "A715": ("A702", "A702"),  # BB
    "A717": ("A703", "A703"),  # DD
    "A718": ("A703", "A703", "A703", "A703"),  # DDDD (SigLA AAF718; not in Unicode)
    "A726": ("A704", "A712", "A712", "A712"),  # EYYY
    "A732": ("A707", "A704"),  # JE
}
LIGATURE_LETTERS = {"ABB": "A714", "BB": "A715", "DD": "A717", "DDDD": "A718", "EYYY": "A726", "JE": "A732"}


def canonical_id(series: str, number: int | str, variant: str | None = None) -> str:
    """"AB" / "A" + 3-digit number + GORILA variant suffix, e.g. AB081, AB131a, A709-2, A506bis.

    The series follows the number (Bennett): AB below 300, A from 301. Sources
    are inconsistent here (Unicode "A028B", SigLA "AB302" for OLE), so the
    `series` argument is not trusted.
    """
    series = "AB" if int(number) < 300 else "A"
    s = f"{series}{int(number):03d}"
    if variant:
        v = variant.strip()
        s += v if v[:1] in "-" else (("-" + v) if v[:1].isdigit() else v.lower() if len(v) == 1 else v)
    return s


def base_id(sign_id: str | None) -> str | None:
    """The sign number without its variant suffix (AB131a -> AB131), for sources that do not
    distinguish variants."""
    if sign_id is None:
        return None
    m = re.match(r"^(AB|A)(\d{3})", sign_id)
    return m.group(0) if m else sign_id


def from_unicode_name(name: str) -> str:
    """Canonical ID from a Unicode Linear A sign name ("LINEAR A SIGN AB131A" -> "AB131a").

    Unicode writes variants in capitals (AB021F, A309A), vessel signs as "A400-VAS",
    fraction signs with their letter ("A707 J") and L variants as "A709-2 L2".
    """
    n = name.removeprefix("LINEAR A SIGN ").split()[0]
    n = n.replace("-VAS", "")
    m = re.fullmatch(r"(AB|A)(\d{3})(-\d)?([A-Z])?", n)
    if not m:
        return n
    ser, num, dash, var = m.groups()
    # Unicode names some variants of shared AB signs in the A series (A028B, A120B, A131C);
    # Bennett/GORILA number AB signs below 300 and Linear A-only signs from *301 up.
    if ser == "A" and int(num) < 300:
        ser = "AB"
    return canonical_id(ser, num, (dash or "") + (var.lower() if var else "")) if (dash or var) else f"{ser}{num}"


def unicode_codepoint(sign_id: str) -> str | None:
    """"U+xxxx" of the Unicode Linear A character for a canonical ID, if Unicode encodes it."""
    return _UNICODE.get(sign_id)


_UNICODE: dict[str, str] = {}
for _o in range(0x10600, 0x10780):
    _n = ud.name(chr(_o), "")
    if _n.startswith("LINEAR A SIGN"):
        _UNICODE[from_unicode_name(_n)] = f"U+{_o:05X}"


def from_sigla_id(sid: str) -> str:
    """Canonical ID from a SigLA sign ID: AB77 -> AB077, AAF707 -> A707, AAF709-2 -> A709-2.

    SigLA's abstract signs (AAP800 num, AAP801 check-mark, AAP802 word-divider,
    AAP803 thumb-print) and unnamed composites (AAZ1000...) have no GORILA
    number; they keep a "SigLA:" prefix so they never collide with one.
    """
    m = re.fullmatch(r"(AB|A|AAF|AAP|AAZ)(\d+)(.*)", sid)
    if not m:
        return f"SigLA:{sid}"
    ser, num, var = m.groups()
    if ser in ("AAP", "AAZ"):
        return f"SigLA:{sid}"
    return canonical_id("A" if ser == "AAF" else ser, num, var or None)


# --- records ------------------------------------------------------------------

ITEM_KINDS = ("word", "logogram", "numeral", "fraction", "transaction", "unknown", "punctuation",
              "divider", "lacuna", "ruling", "vacat", "other", "mixed")
ROLES = ("syllabogram", "logogram", "fraction", "transaction", "punctuation", "unknown", None)


@dataclass
class Token:
    written_as: str  # the source's own encoding: Unicode name, SigLA ID, Younger value
    sign_id: str | None  # L0 canonical ID; None if unidentified or not yet mapped (Younger: A1.8)
    role: str | None = None  # see ROLES; None if the source does not say
    components: list[str] = field(default_factory=list)  # ligature / composite components (L0 IDs)
    l1_value: str | None = None  # conventional value AS PRINTED by the source (Younger only)
    l1: str | None = None  # uniform L1 value from sign_id (aegean.corpus.layers; A1.8)
    unidentified: bool = False
    doubtful: bool | None = None  # reading doubtful (SigLA unsure-reading; Younger underline)
    erased: bool | None = None
    restored: bool | None = None  # editorial restoration as marked by the source (Younger < >)
    conjectural: bool | None = None  # the source's own conjecture (Younger green)
    break_before: str | None = None  # "" | "]" | "]-" ; None if not recorded
    break_after: str | None = None  # "" | "[" | "-["
    stacked: bool | None = None  # written stacked with a neighbour; None = not recorded by the source
    bbox: tuple[int, int, int, int] | None = None  # SigLA drawing coordinates
    flags: list[str] = field(default_factory=list)


@dataclass
class Item:
    kind: str  # see ITEM_KINDS
    tokens: list[Token] = field(default_factory=list)
    numeral_value: int | None = None  # additive integer value of a numeral item (exact)
    divider_after: bool | None = None  # followed by a word divider
    left_break: str | None = None  # group-level break as the source marks it
    right_break: str | None = None
    lacuna_estimate: int | None = None  # signs estimated lost (Younger "[ • • • ]")
    raw: str = ""
    flags: list[str] = field(default_factory=list)


@dataclass
class Line:
    index: int
    ref: str | None  # the source's line reference ("a.1", ".3-4"); None if the source has none
    ref_kind: str  # "physical" (side.line after GORILA) | "entry" (lineara.xyz entry lines) | "none"
    ruling_before: bool | None = None  # a ruled line precedes this line
    items: list[Item] = field(default_factory=list)


@dataclass
class Witness:
    source: str
    source_id: str
    source_version: str  # pinned snapshot hash prefix
    side: str | None
    layer: str  # "L0" (sign IDs) or "L0+L1" (Younger: L1 values, L0 where the value is a sign number)
    lines: list[Line] = field(default_factory=list)
    period: str | None = None  # as the source gives it
    scribe: str | None = None  # as the source gives it
    notes: list[str] = field(default_factory=list)  # the source's commentary (not data)
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def tokens(self):
        for ln in self.lines:
            for it in ln.items:
                yield from it.tokens


def validate(w: Witness) -> list[str]:
    """Structural checks; returns a list of problems (empty if valid)."""
    errs = []
    if w.layer not in ("L0", "L0+L1"):
        errs.append(f"bad layer {w.layer}")
    for ln in w.lines:
        if ln.ref_kind not in ("physical", "entry", "none"):
            errs.append(f"line {ln.index}: bad ref_kind {ln.ref_kind}")
        for it in ln.items:
            if it.kind not in ITEM_KINDS:
                errs.append(f"line {ln.index}: bad item kind {it.kind}")
            if it.kind == "numeral" and it.numeral_value is None and "unparsed_number" not in it.flags:
                errs.append(f"line {ln.index}: numeral without value: {it.raw!r}")
            for t in it.tokens:
                if t.role not in ROLES:
                    errs.append(f"line {ln.index}: bad role {t.role}")
                if t.sign_id is not None and not re.match(r"^(AB|A)\d{3}|^SigLA:", t.sign_id):
                    errs.append(f"line {ln.index}: non-canonical sign_id {t.sign_id!r}")
                if t.unidentified and t.sign_id is not None:
                    errs.append(f"line {ln.index}: unidentified token with a sign_id")
    return errs
