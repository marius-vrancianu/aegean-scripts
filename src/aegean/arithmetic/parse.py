"""A2.1 — parse L0 document lines into entries (label + quantity).

Fraction signs stay symbolic (J, E, L2, JE...). This module assigns no
fraction values: value sets are inputs to the checker (A2.6), never defaults
here, so no published value set can leak into parsing.

Entry rule (per line, left to right):
- sign-groups accumulate into the current label;
- a numeral token starts a quantity; fraction tokens directly after it join it;
- a fraction token with no preceding numeral starts a fraction-only quantity;
- the next sign-group after a quantity starts a new label.
A quantity with no label on its own line gets `label_on_line=False`; resolving
such cases (continuation lines, column layouts) is left to the scope rules,
which are frozen with the hypotheses (A2.5), not guessed here.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Sign IDs of the accounting words, by Bennett/GORILA number:
# KU = AB081, RO = AB002, KI = AB067, PO = AB011, TO = AB005.
MARKERS = {
    ("AB081", "AB002"): "KU-RO",
    ("AB067", "AB002"): "KI-RO",
    ("AB011", "AB005", "AB081", "AB002"): "PO-TO-KU-RO",
}


@dataclass
class Quantity:
    integer: int | None
    fractions: list[str] = field(default_factory=list)
    damaged: bool = False
    flags: list[str] = field(default_factory=list)


@dataclass
class Entry:
    line: int  # 0-based index into Document.lines
    label: list[tuple[str, ...]]  # sign-groups before the quantity on this line
    quantity: Quantity
    marker: str | None = None  # KU-RO / KI-RO / PO-TO-KU-RO if the label contains one
    label_on_line: bool = True


def _tok(t, key):
    return t[key] if isinstance(t, dict) else getattr(t, key)


def _damaged(t) -> bool:
    return bool(_tok(t, "damaged_left") or _tok(t, "damaged_right") or _tok(t, "flags"))


def parse_line(tokens, line_no: int) -> tuple[list[Entry], list[str]]:
    """Return (entries, warnings) for one line of tokens (dicts or Token objects)."""
    entries: list[Entry] = []
    warnings: list[str] = []
    label: list[tuple[str, ...]] = []
    current: Quantity | None = None
    prev_lacuna = False

    def close():
        nonlocal current, label
        if current is not None:
            marker = next((MARKERS[g] for g in label if g in MARKERS), None)
            entries.append(Entry(line_no, label, current, marker, label_on_line=bool(label)))
            current, label = None, []

    for t in tokens:
        ty = _tok(t, "type")
        if ty == "group":
            close()
            label.append(tuple(_tok(t, "signs")))
            prev_lacuna = False
        elif ty == "numeral":
            if current is not None:
                warnings.append(f"line {line_no}: consecutive numerals")
                close()
            current = Quantity(integer=_tok(t, "value"), damaged=_damaged(t) or prev_lacuna)
            prev_lacuna = False
        elif ty == "fraction":
            if current is None:
                current = Quantity(integer=None, damaged=prev_lacuna)
            current.fractions.extend(_tok(t, "fractions"))
            current.damaged = current.damaged or _damaged(t)
            prev_lacuna = False
        elif ty == "lacuna":
            if current is not None:
                current.damaged = True
            prev_lacuna = True
        elif ty == "separator":
            continue
        else:  # other / mixed: keep visible, never silently dropped
            if current is not None:
                current.flags.append(f"next_to_{ty}")
                current.damaged = True
            warnings.append(f"line {line_no}: {ty} token {_tok(t, 'raw')!r}")
    close()
    return entries, warnings


def parse_document(doc) -> tuple[list[Entry], list[str]]:
    lines = doc["lines"] if isinstance(doc, dict) else doc.lines
    entries: list[Entry] = []
    warnings: list[str] = []
    for i, ln in enumerate(lines):
        e, w = parse_line(ln, i)
        entries += e
        warnings += w
    return entries, warnings
