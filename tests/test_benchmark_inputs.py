"""Benchmark inputs (A5.17): Linear A sign-groups from witness records, Linear B control words. Synthetic fixtures."""
import unicodedata

import pytest

from aegean.benchmark import inputs, nulls
from aegean.benchmark.interface import Lexicon

import random


def tok(l1, sign_id="AB001", **kw):
    return {"sign_id": sign_id, "l1": l1, **kw}


def item(kind, toks, **kw):
    return {"kind": kind, "tokens": toks, **kw}


def witness(items, doc="AA 1", source="sigla"):
    return {"source": source, "source_id": doc, "doc_key": doc, "lines": [{"items": items}]}


def test_linear_a_groups_keeps_only_complete_multi_sign_words():
    w = witness([
        item("word", [tok("ku"), tok("RO")]),                                    # kept, upper-cased
        item("word", [tok("KU")]),                                               # one sign
        item("logogram", [tok("*131a"), tok("RO")]),                             # not a word
        item("word", [tok("KU"), tok("RO")], left_break="]"),                    # broken edge (group)
        item("word", [tok("KU"), tok("RO", break_after=True)]),                  # broken edge (sign)
        item("word", [tok("KU"), {"sign_id": None, "l1": None, "unidentified": True}]),  # unidentified sign
        item("word", [tok("DA"), tok("RE"), tok("J", sign_id="A707")]),          # fraction sign removed
        item("word", [tok("*301"), tok("NA")]),                                  # no Linear B value: kept here,
    ])                                                                           # eligibility is the method's
    assert inputs.linear_a_groups([w]) == [("AA 1", ("KU", "RO")), ("AA 1", ("DA", "RE")), ("AA 1", ("*301", "NA"))]
    assert inputs.unique([("B",), ("A",), ("B",)]) == [("A",), ("B",)]


def test_parse_cog_converts_linear_b_signs_to_unicode_values():
    lb = lambda *names: "".join(unicodedata.lookup(f"LINEAR B {n}") for n in names)
    ko, no, so, a = "SYLLABLE B070 KO", "SYLLABLE B052 NO", "SYLLABLE B012 SO", "SYLLABLE B008 A"
    text = ("linear_b\tgreek\n"
            f"{lb(ko, no, so)}\tκνωσος\n"
            f"{lb(a, ko)}\tx|y\n"
            f"{lb(ko)}\tx\n"                         # one sign
            f"{lb(ko, no)}\t_\n"                     # no Greek counterpart
            f"{lb(ko, 'SYMBOL B018')}\tx\n"          # a sign without a value
            f"{lb(ko)}z\tx\n")                       # not Linear B
    words, dropped = inputs.parse_cog(text)
    assert words == [("KO", "NO", "SO"), ("A", "KO"), ("KO", "*18")]
    assert dropped == {"no_greek": 1, "non_linear_b_sign": 1, "too_short": 1}
    with pytest.raises(ValueError):
        inputs.parse_cog("a\tb\n")


needs_control = pytest.mark.skipif(not inputs.ND_COG.exists(), reason="run python data/raw/neurodecipher/fetch.py")


@needs_control
def test_linear_b_control_file():
    words, meta = inputs.linear_b_control()
    assert len(words) == 918 and meta["dropped"] == {"no_greek": 0, "non_linear_b_sign": 0, "too_short": 1}
    assert ("KO", "NO", "SO") in words and ("PA", "I", "TO") in words  # Knossos, Phaistos


def test_pseudo_lexicon_matches_size_lengths_and_letters():
    real = Lexicon("r", frozenset({"KTP", "SMR", "DPR", "NTN", "HMR", "PN", "KR", "TRKM"}))
    a = nulls.pseudo_lexicon(real, random.Random(1), index=0)
    b = nulls.pseudo_lexicon(real, random.Random(1))
    assert a.forms == b.forms and a.kind == "null" and len(a) == len(real)
    assert {len(f) for f in a.forms} <= {2, 3, 4} and set("".join(a.forms)) <= set("".join(real.forms))
    assert len(nulls.pseudo_lexicon(real, random.Random(2), 2.0)) == 16
    with pytest.raises(ValueError):
        nulls.pseudo_lexicon(Lexicon("tiny", frozenset({"AA"})), random.Random(1), 4.0)  # only one form exists


def test_pseudo_lexicon_letter_frequencies_follow_the_real_lexicon():
    real = Lexicon("r", frozenset({"KKK" + c for c in "ABCDEFGH"}))  # K is 3/4 of all letters
    rng = random.Random(5)
    letters = "".join(f for _ in range(40) for f in nulls.pseudo_lexicon(real, rng).forms)
    # a little under 3/4: duplicate forms are redrawn, which thins out the commonest letter
    assert 0.62 < letters.count("K") / len(letters) < 0.76


def test_matched_lexicon_has_the_real_lexicon_size_after_expansion_and_its_positional_letters():
    from aegean.benchmark.m1 import M1
    m = M1()
    real = Lexicon("r", frozenset({"KWP", "SWR", "DWR", "NWN", "HWR", "TWM", "KWS", "PWD", "MWT", "RWK", "SD", "TN"}))
    target = len(m.prepare(real))
    assert target > len(real)  # S, D and T interchange, so the method sees more forms than the lexicon lists
    for seed in range(5):
        fake = nulls.matched_lexicon(real, m, random.Random(seed), seed)
        assert len(m.prepare(fake)) == target and fake.kind == "null"
        assert all(f[1] == "W" for f in fake.forms if len(f) == 3)  # W is always medial in the real lexicon
    a, b = (nulls.matched_lexicon(real, m, random.Random(9)) for _ in range(2))
    assert a.forms == b.forms


def test_random_sign_strings():
    out = nulls.random_sign_strings([2, 3, 5], ["KA", "KA", "RO"], random.Random(3))
    assert [len(g) for g in out] == [2, 3, 5] and {s for g in out for s in g} <= {"KA", "RO"}
    with pytest.raises(ValueError):
        nulls.random_sign_strings([2], [], random.Random(3))
