"""A2.1 parser fixtures.

Hand-checked fixtures: each states the document, the expected parse and the
source used to check it. "GORILA facsimile" = the GORILA I drawing as
published in the lineara.xyz images folder at commit 9c81beba, viewed
2026-11-04 by Claude (an LLM reading stroke counts; Rule 5 applies: these are
checks, not authority). Units are vertical strokes, tens dots or short
horizontal strokes, hundreds circles.
"""
import json
from pathlib import Path

import pytest

from aegean.arithmetic.parse import parse_document, parse_line
from aegean.corpus.lineara import tokenize

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "data/processed/corpus-v0.1/documents.jsonl"
KU, RO = "\U00010642", "\U00010601"
J, E = "\U00010746", "\U00010743"
LAC = "\U0001076b"


def n(v):
    """Aegean-number token for an integer < 100."""
    tens, units = divmod(v, 10)
    s = (chr(0x1010F + tens) if tens else "") + (chr(0x10106 + units) if units else "")
    return s


def toks(*raws):
    return [tokenize(r) for r in raws]


def test_numeral_helper():
    assert tokenize(n(45)).value == 45 and tokenize(n(9)).value == 9


def test_entry_with_fraction_and_total_marker():
    e, w = parse_line(toks("\U00010600", n(45), J), 0)
    assert len(e) == 1 and e[0].quantity.integer == 45 and e[0].quantity.fractions == ["J"]
    e, _ = parse_line(toks(KU + RO, n(95)), 4)
    assert e[0].marker == "KU-RO" and e[0].quantity.integer == 95 and not w


def test_fraction_only_and_multiple_fractions_stay_symbolic():
    e, _ = parse_line(toks("\U00010600", J, E), 0)
    q = e[0].quantity
    assert q.integer is None and q.fractions == ["J", "E"]


def test_damage_propagates():
    e, _ = parse_line(toks("\U00010600", n(2) + LAC), 0)
    assert e[0].quantity.damaged
    e, _ = parse_line(toks("\U00010600", LAC, n(2)), 0)
    assert e[0].quantity.damaged


def test_unlabelled_quantity_is_marked():
    e, _ = parse_line(toks(n(2)), 1)
    assert not e[0].label_on_line and e[0].label == []


needs_corpus = pytest.mark.skipif(not CORPUS.exists(), reason="run `python -m aegean.corpus.build` first")


def _doc(doc_id):
    for line in CORPUS.open(encoding="utf-8"):
        d = json.loads(line)
        if d["id"] == doc_id:
            return d
    raise KeyError(doc_id)


def _summary(entries):
    return [(e.marker, e.quantity.integer, e.quantity.fractions) for e in entries]


@needs_corpus
def test_HT104_gorila_facsimile():
    # GORILA facsimile: lines with 4 dots + 5 strokes + J; (damaged band) 2 dots + J;
    # 2 dots + 9 strokes; KU-RO + 9 dots + 5 strokes.
    # Confidence: high for 45 J and KU-RO 95; medium for 20 J and 29 (stippled damage band).
    e, w = parse_document(_doc("HT104"))
    assert _summary(e) == [(None, 45, ["J"]), (None, 20, ["J"]), (None, 29, []), ("KU-RO", 95, [])]


@needs_corpus
def test_HT13_total_gorila_facsimile():
    # GORILA facsimile, last line: KU-RO, one circle (100), three dots (30), J. Confidence high.
    e, _ = parse_document(_doc("HT13"))
    assert _summary(e)[-1] == ("KU-RO", 130, ["J"])


@needs_corpus
def test_HT122a_total_and_broken_corner():
    # GORILA facsimile: top-left corner broken (lineara's U+1076B at line 1 start);
    # penultimate line KU-RO, three horizontal tens strokes and one unit (31). Confidence high.
    e, _ = parse_document(_doc("HT122a"))
    totals = [x for x in e if x.marker == "KU-RO"]
    assert [(t.quantity.integer, t.quantity.fractions) for t in totals] == [(31, [])]
    assert e[0].quantity.damaged
