"""Method M2 (A5.17): Dolgopolsky sound-class skeleton matching. Expected values checked by hand against the
class table in m2.py (LingPy DOLGO model, Dolgopolsky 1986)."""
import random

import pytest

from aegean.benchmark import lexicons, nulls
from aegean.benchmark.interface import DOF_ITEMS, Lexicon, normalise
from aegean.benchmark.m2 import M2, M2Rules, SIGN_DOLGO, levenshtein
from aegean.corpus.layers import LB_VALUES


def test_every_unicode_linear_b_value_has_a_class():
    assert set(LB_VALUES.values()) <= set(SIGN_DOLGO)


@pytest.mark.parametrize("group, want", [
    ("KU-RO", "KR"),
    ("DA-RE", "TR"),          # d is T
    ("QE-TO", "KT"),          # labiovelar q is K
    ("ZA-KA", "SK"),          # z at its letter value
    ("A-TA-NA", "TN"),        # a pure vowel sign gives nothing
    ("A2-KA", "HK"),          # a2 is ha
    ("DWE-NWA-PTE", "TWNWPT"),
    ("TA2-RA2-RO2-RA3", "TJRJRJR"),
    ("PU2-A3-AU", "P"),
])
def test_skeleton(group, want):
    assert M2().skeleton(normalise(group)) == want


def test_eligibility():
    m = M2()
    assert m.eligible(normalise("KU-RO")) and not m.eligible(normalise("*301-NA"))   # no Linear B value
    assert not m.eligible(normalise("A-KA")) and not m.eligible(normalise("KA"))      # one class; one sign


def test_levenshtein():
    assert levenshtein("KRT", "KRT") == 0 and levenshtein("KRT", "KR") == 1 and levenshtein("KRT", "PRS") == 2
    assert levenshtein("", "AB") == 2


def test_threshold_quarter():
    m = M2()                      # max_distance 1/4
    lex = m.prepare(Lexicon("x", frozenset({"KRTS", "PNM", "KR"})))
    assert m.hits([normalise("KU-RO")], lex) == [True]                    # exact KR
    assert m.hits([normalise("KU-RA-TA")], lex) == [True]                 # KRT -> KRTS: 1 edit / 4
    assert m.hits([normalise("PA-NA-SA")], lex) == [False]                # PNS vs PNM: 1 edit / 3 > 1/4
    assert m.hits([normalise("KA-RA-PA-SA")], lex) == [True]              # KRPS vs KRTS: 1 / 4
    assert m.match(normalise("KU-RA-TA"), lex).form == "KRTS"


@pytest.mark.parametrize("theta", [0.0, 0.25, 1 / 3])
def test_reach_equals_brute_force(theta):
    """skeletons() is exactly the set of strings (up to 5 classes) within the bound, so hits() equals match()."""
    import itertools
    m = M2(M2Rules(max_distance=theta))
    space = ["".join(p) for n in range(1, 5) for p in itertools.product("PTKR", repeat=n)]
    for g in ("KU-RO", "KU-RA-TA", "PA-TA-KA-RA", "TA-TA"):
        sk = m.skeleton(normalise(g))
        brute = {x for x in space if levenshtein(sk, x) <= theta * max(len(sk), len(x))}
        assert brute == {x for x in m.skeletons(normalise(g)) if x in set(space)}, (g, theta)


def test_no_lexicon_side_licences_and_null_compatibility():
    m = M2()
    real = Lexicon("r", frozenset({"KRT", "PNM", "SKR", "TRK", "KR", "MRTS"}))
    assert m.prepare(real) == real.forms                      # no interchanges: expansion is the identity
    fake = nulls.stratified_matched_lexicon(real, m, random.Random(3))
    assert sorted(map(len, fake.forms)) == sorted(map(len, real.forms))


def test_degrees_of_freedom():
    dof = M2().degrees_of_freedom()
    assert set(DOF_ITEMS) <= set(dof) and dof["edit_distance"]["max_normalised"] == 0.25
    assert dof["affix_menus"] == {"prefixes": 0, "suffixes": 0}


needs = pytest.mark.skipif(not (lexicons.HEBREW_XML.exists() and lexicons.CMUDICT.exists()
                                and lexicons.ZEMBEREK_DICT.exists() and lexicons.TR_FREQ.exists()),
                           reason="lexicon sources not fetched")


@needs
def test_dolgo_lexicons():
    h, e, t = (lexicons.REGISTRY[k]() for k in ("hebrew-strong-verbs-dolgo", "english-verbs-dolgo", "turkish-verbs-dolgo"))
    assert (len(h), len(e), len(t)) == (428, 502, 502)
    assert "D" not in "".join(h.forms | e.forms | t.forms)               # d merged into T
    assert lexicons.english_skeleton(["JH", "AH", "JH"], lexicons.ENGLISH_DOLGO) == "KK"   # judge: affricates K
    assert lexicons.english_skeleton(["HH", "AE", "V"], lexicons.ENGLISH_DOLGO) == "HW"   # have: v is W
    assert lexicons.turkish_skeleton("çekmek", lexicons.TURKISH_DOLGO) == "KK"
    assert lexicons.turkish_skeleton("vermek", lexicons.TURKISH_DOLGO) == "WR"
