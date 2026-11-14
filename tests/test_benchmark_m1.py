"""M1 is a faithful port of the Finding 001 matcher (A5.12).

The original script (experiments/finding-001/original/nulltest.py) is loaded as
it is, against a small made-up lexicon in a temporary HOME, and both
implementations are run on the same sign strings. With the pinned Hebrew
lexicon present, the figures of Finding 001 that do not depend on the Linear A
word list are checked as well.
"""
import importlib.util
import json
import random
import re
from pathlib import Path

import pytest

from aegean.benchmark import lexicons, nulls
from aegean.benchmark.interface import Lexicon, normalise
from aegean.benchmark.m1 import M1, M1Rules, PREFIXES, SUFFIXES

REPO = Path(__file__).resolve().parents[1]
ORIGINAL = REPO / "experiments/finding-001/original"
# Made-up "verbs": enough roots of each length to give both hits and misses.
FAKE_ROOTS = ["כתב", "שמר", "דבר", "נתן", "אמר", "בוא", "ראה", "ידע", "קום", "שוב", "מלך", "זכר", "טוב", "גדל",
              "צדק", "פקד", "בן", "קל", "תרגם", "שחרר"]
SIGNS = ["A", "E", "I", "O", "U", "AU", "A3", "AI", "A2", "*301", "*56", "PU2", "RA2", "TA2", "NWA", "DWE", "PTE",
         "DA", "DI", "TA", "TI", "TU", "TE", "KA", "KI", "KU", "QA", "PA", "PI", "SA", "SI", "SE", "ZA", "RA", "RU",
         "MA", "ME", "MI", "NA", "NE", "NU", "JA", "WA", "WI"]


@pytest.fixture(scope="module")
def original(tmp_path_factory):
    home = tmp_path_factory.mktemp("home")
    (home / "yadiktu").mkdir()
    xml = "\n".join(f'<entry><w pos="v" pron="x" xlit="x" xml:lang="heb">{r}</w></entry>' for r in FAKE_ROOTS)
    (home / "yadiktu/HebrewStrong.xml").write_text(xml, encoding="utf-8")
    mp = pytest.MonkeyPatch()
    mp.setenv("HOME", str(home))
    spec = importlib.util.spec_from_file_location("finding001_nulltest", ORIGINAL / "nulltest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mp.undo()
    return mod, xml


def as_tuple(match):
    return None if match is None else (match.analysis["prefix"], match.analysis["core"], match.analysis["suffix"], match.form)


def test_lexicon_conversion_and_expansion_equal_the_original(original):
    mod, xml = original
    forms = lexicons.hebrew_verb_skeletons(xml)
    assert forms == frozenset(mod.roots) and len(forms) >= 15
    assert M1().prepare(Lexicon("fake", forms)) == frozenset(mod.R)


def test_port_returns_the_same_parse_as_the_original_on_random_sign_strings(original):
    mod, xml = original
    m = M1()
    prepared = m.prepare(Lexicon("fake", lexicons.hebrew_verb_skeletons(xml)))
    rng = random.Random(20261114)
    menu = [s for g in PREFIXES + SUFFIXES for s in g]
    strings = ["-".join(rng.choice(SIGNS + menu) for _ in range(rng.randint(1, 7))) for _ in range(6000)]
    strings += ["A-TA-I-*301-WA-JA", "JA-DI-KI-TU", "JA-SA-SA-RA-ME", "U-NA-KA-NA-SI", "I-PI-NA-MA", "SI-RU-TE",
                "TA-NA-RA-TE-U-TI-NU", "KA-KA", "A-A", "TA-TA-NA"]
    hits = 0
    for w in strings:
        g = normalise(w)
        want = mod.parse(w)
        assert as_tuple(m.match(g, prepared)) == want, w
        assert m.hits([g], prepared)[0] == (want is not None), w
        hits += want is not None
        assert m.eligible(g) == (len(g) >= 2 and all(mod.cons(s) != "?" for s in g)), w
    assert 0.02 < hits / len(strings) < 0.98  # the comparison exercised both outcomes


def test_sign_classes():
    m = M1()
    assert m.sign_class("*301") == "N" and m.sign_class("QA") == "K" and m.sign_class("ZU") == "S"
    assert m.sign_class("A") is None and m.sign_class("AI") is None
    assert m.sign_class("*56") == "?" and m.sign_class("A2") == "?"  # kept from the original (see m1.py)
    assert not m.eligible(("KA",)) and not m.eligible(("KA", "*56")) and m.eligible(("ka".upper(), "RO"))


def test_lower_case_input_is_normalised():
    """run.py passed lower-case Linear B words, so the upper-case menus never matched (Finding 001 addendum)."""
    assert normalise("ko-no-so") == ("KO", "NO", "SO") == normalise(["ko", "NO", "so"])


def test_variants_and_weak_radical():
    m = M1()
    assert m.variants("SD") == {"SD", "ST", "TD", "TT"}
    assert set(m.core_skeletons(("KA", "RA"))) == {"KR"} | {"KR"[:i] + w + "KR"[i:] for i in range(3) for w in "HWJ"}
    # doubled sign collapses; the vowel sign is H or nothing; the two-consonant reading KH takes a weak radical
    assert set(m.core_skeletons(("KA", "KA", "A"))) == {"K", "KH"} | {"KH"[:i] + w + "KH"[i:] for i in range(3) for w in "HWJ"}


def test_rules_round_trip_and_override(tmp_path):
    assert M1Rules.from_json(_write(tmp_path, M1Rules().to_json())) == M1Rules()
    r = M1Rules.from_json(_write(tmp_path, {"prefixes": [], "suffixes": ["u-ti-nu"], "weak_radicals": ""}))
    assert r.prefixes == () and r.suffixes == (("U", "TI", "NU"),) and r.max_core == 4
    strict = M1(r)
    assert all(len(s) != 3 for s in strict.core_skeletons(("KA", "RA")))
    with pytest.raises(ValueError):
        M1Rules.from_json(_write(tmp_path, {"prefixs": []}))


def _write(tmp_path, obj):
    p = tmp_path / "rules.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_degrees_of_freedom_cover_the_guardrail_checklist():
    from aegean.benchmark.interface import DOF_ITEMS
    dof = M1().degrees_of_freedom()
    assert set(dof) == set(DOF_ITEMS)
    assert dof["affix_menus"] == {"prefixes": 12, "suffixes": 16, "segmentations_at_most": 221}


needs_hebrew = pytest.mark.skipif(not lexicons.HEBREW_XML.exists(),
                                  reason="run python data/raw/openscriptures-HebrewLexicon/fetch.py")


@needs_hebrew
def test_finding_001_figures_that_do_not_need_the_linear_a_word_list():
    m = M1()
    lex = lexicons.hebrew_strong_verbs()
    prepared = m.prepare(lex)
    assert len(lex) == 502  # Finding 001, Data
    io_za_2 = ["A-TA-I-*301-WA-JA", "JA-DI-KI-TU", "JA-SA-SA-RA-ME", "U-NA-KA-NA-SI", "I-PI-NA-MA", "SI-RU-TE",
               "TA-NA-RA-TE-U-TI-NU"]
    assert all(m.match(normalise(w), prepared) for w in io_za_2)  # Finding 001, sanity check
    lb = re.search(r"LB='''(.*?)'''", (ORIGINAL / "run.py").read_text(encoding="utf-8"), re.S).group(1).split()
    groups = [normalise(w) for w in lb]
    # Finding 001 counted words the method cannot read (here e-ma-a2) as misses; `hits` does the same.
    assert len(groups) == 79 and sum(m.eligible(g) for g in groups) == 78
    assert round(sum(m.hits(groups, prepared)) / 79, 3) == 0.734  # Finding 001, Results
    # run2.py's stream: random.seed(7), then 20 pseudo-lexicons. Its Linear B column was printed, not published.
    rng = random.Random(7)
    rates = [sum(m.hits(groups, m.prepare(nulls.pseudo_lexicon(lex, rng)))) / 79 for _ in range(20)]
    assert (round(sum(rates) / 20, 3), round(min(rates), 3), round(max(rates), 3)) == (0.710, 0.620, 0.759)
