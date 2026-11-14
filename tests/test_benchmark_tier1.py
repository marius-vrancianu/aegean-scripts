"""The Tier 1 runner (A5.17) on synthetic corpora with a known answer.

No real Linear A is used here: a run on the corpus belongs to a registered
hypothesis (hypotheses/H-A5-01.md), not to the test suite.
"""
import json
import random

import pytest

from aegean.benchmark import tier1
from aegean.benchmark.interface import Lexicon
from aegean.benchmark.m1 import M1

CONS = "KTPDSRMN"
VOWELS = "AEIOU"


def make_corpus(seed, n_docs=60, sources=("sigla", "lineara.xyz")):
    """Random CV sign-groups of 2-5 signs, the same text in each source, three sites."""
    rng = random.Random(seed)
    ws = []
    for d in range(n_docs):
        key = f"{('AA', 'BB', 'CC')[d % 3]} {d}"
        items = [{"kind": "word", "tokens": [{"sign_id": "AB001", "l1": rng.choice(CONS) + rng.choice(VOWELS)}
                                             for _ in range(rng.randint(2, 5))]} for _ in range(6)]
        for s in sources:
            ws.append({"source": s, "source_id": key, "doc_key": key, "lines": [{"items": items}]})
    return ws


def groups_of(ws):
    return sorted({tuple(t["l1"] for t in it["tokens"]) for w in ws for ln in w["lines"] for it in ln["items"]})


def test_compare_p_values():
    c = tier1.compare(0.5, [0.1, 0.2, 0.5, 0.9])
    assert c["p"] == pytest.approx(3 / 5) and c["p_lower"] == pytest.approx(4 / 5)
    assert c["false_positive_rate"] == pytest.approx(0.425) and c["excess"] == pytest.approx(0.075)
    assert tier1.compare(1.0, [0.0] * 999)["p"] == pytest.approx(1 / 1000)  # smallest attainable p


def test_label_follows_the_decision_rule():
    assert tier1.label(0.20, 0.50).startswith("A")
    assert tier1.label(0.05, 0.05).startswith("C")
    assert tier1.label(0.01, 0.051).startswith("B: above the null")
    assert tier1.label(0.051, 0.01).startswith("B: differs")


def test_bh_adjust():
    assert tier1.bh_adjust([0.01, 0.04, 0.03, 0.20]) == pytest.approx([0.04, 0.04 * 4 / 3, 0.04 * 4 / 3, 0.20])
    assert tier1.bh_adjust([0.03]) == [0.03]


def test_hit_table_equals_direct_computation():
    m = M1()
    gs = groups_of(make_corpus(1))
    real = Lexicon("r", frozenset({"KTP", "SMR", "DPR", "NTN", "KR", "TM", "PSRK"}))
    null = tier1.null_lexicons(real, 5, 9)
    table = tier1.HitTable(m, gs, real, null)
    sub = gs[::3]
    assert table.rates(sub)[0] == len(sub)
    c = table.compare(sub)
    assert c["n"] == len(sub)
    assert c["real"] == pytest.approx(tier1.hit_rate(m, sub, m.prepare(real)))
    assert c["false_positive_rate"] == pytest.approx(sum(tier1.hit_rate(m, sub, m.prepare(l)) for l in null) / 5)
    assert sum(v["n"] for v in table.by_length(sub).values()) == len(sub)
    with pytest.raises(ValueError):
        table.compare([("*56", "*79")])


def test_difference_test_removes_a_shift_common_to_input_and_control():
    """A lexicon that is simply larger than the null beats it everywhere: test 1 fires, test 2 does not."""
    m = M1()
    gs = groups_of(make_corpus(11))
    control = groups_of(make_corpus(12, sources=("sigla",)))
    base = sorted(a + b + c for a in "KTPRSMN" for b in "KTPRSMN" for c in "KTPRSMN")
    real = Lexicon("big", frozenset(base))                      # the "real" lexicon: all 343 forms
    null = [Lexicon(f"n{i}", frozenset(random.Random(i).sample(base, 60))) for i in range(99)]  # far smaller
    table, ctable = tier1.HitTable(m, gs, real, null), tier1.HitTable(m, control, real, null)
    assert table.compare(gs)["p"] == pytest.approx(1 / 100)
    d = tier1.difference_test(table, gs, tier1.Control(ctable, control))
    assert d["excess_linear_a"] > 0.1 and d["excess_control"] > 0.1 and d["p"] > 0.05


def test_control_standardisation_reweights_by_length():
    m = M1()
    control = [("KA", "TA"), ("KA", "RA"), ("KA", "TA", "PA"), ("MA", "NA", "SA", "RA", "TA")]
    real = Lexicon("r", frozenset({"KT", "KTP"}))
    c = tier1.Control(tier1.HitTable(m, control, real, [Lexicon("n", frozenset({"KR"}))]), control)
    assert c.standardised({2: 1, 3: 1})[0] == pytest.approx((0.5 + 1.0) / 2)
    assert c.standardised({2: 3, 3: 1, 4: 5})[::2] == (pytest.approx((3 * 0.5 + 1.0) / 4), [2, 3])  # no 4-sign control
    with pytest.raises(ValueError):
        c.standardised({4: 2})


def test_null_lexicons_are_one_seeded_stream():
    real = Lexicon("r", frozenset({"KTP", "SMR", "DPR", "NTN", "KR"}))
    a, b = tier1.null_lexicons(real, 4, 3), tier1.null_lexicons(real, 6, 3)
    assert [l.forms for l in a] == [l.forms for l in b[:4]] and a[0].forms != a[1].forms


def run_small(ws, real, control, **kw):
    return tier1.run(M1(), real, ws, control, protocol="H-A5-00", n_null=99, n_resample=20, **kw)


def lexicon_fitting(groups, n, seed):
    """n roots that each fit a sign-group without any licence (no affix, no weak radical): a planted language."""
    m = M1()
    rng = random.Random(seed)
    roots = sorted({"".join(m.sign_class(s) for s in g) for g in groups if 3 <= len(g) <= 4})
    return Lexicon("planted", frozenset(rng.sample(roots, n)))


def test_planted_lexicon_is_detected_and_a_random_one_is_not():
    """Known answer: the benchmark separates a lexicon the sign-groups were built to match from noise."""
    ws = make_corpus(2)
    control = groups_of(make_corpus(3, sources=("sigla",)))  # unrelated strings of the same kind
    real = lexicon_fitting(groups_of(ws), 60, 4)
    r = run_small(ws, real, control)
    assert r["test1"]["p"] == pytest.approx(1 / 100) and r["test1"]["excess"] > 0.05
    assert r["test2"]["p"] == pytest.approx(1 / 100) and r["test2"]["difference"] > 0.05
    assert r["control"]["p"] > 0.05
    assert r["outcome"].startswith("C")
    assert r["resampling"]["share_of_draws"]["p1_at_most_alpha"] > 0.9
    assert {len(M1().prepare(l)) for l in tier1.matched_lexicons(real, M1(), 5, 1)} == {len(M1().prepare(real))}

    noise = tier1.matched_lexicons(real, M1(), 1, 77)[0]
    r0 = run_small(ws, Lexicon("noise", noise.forms), control)
    assert r0["linear_a"]["primary"]["p"] > 0.05 and r0["outcome"].startswith("A")


def test_lexicon_that_fits_the_control_too_is_outcome_b():
    ws = make_corpus(2)
    control = groups_of(make_corpus(3, sources=("sigla",)))
    real = lexicon_fitting(groups_of(ws) + control, 120, 4)
    r = run_small(ws, real, control)
    assert r["test1"]["p"] <= 0.05 < r["test2"]["p"] and r["outcome"].startswith("B: above the null")


def test_run_is_deterministic_and_reports_every_section():
    ws = make_corpus(5, n_docs=30)
    control = groups_of(make_corpus(6, n_docs=20, sources=("sigla",)))
    real = Lexicon("r", frozenset({"KTP", "SMR", "DPR", "NTN", "KR", "TM", "PSRK", "MNT", "RKS"}))
    a, b = run_small(ws, real, control), run_small(ws, real, control)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["params"]["split"] == "train" and a["protocol"] == "H-A5-00"
    assert set(a["linear_a"]) == {"primary", "sigla", "lineara.xyz"}  # no Younger witnesses in this corpus
    assert a["inputs"]["younger"]["eligible"] == 0
    assert set(a["lexicon_size"]) == {"0.5", "1", "2", "4"}
    assert a["lexicon_size"]["4"]["mean"] >= a["lexicon_size"]["0.5"]["mean"]  # more forms, more false matches
    assert a["permissiveness"]["readings_per_group_mean"] >= 1
    text = tier1.report(a, {"corpus": "synthetic", "commit": "0000000"})
    for heading in ("## Outcome", "## By length", "## The Finding 001 null", "## Sensitivity", "## Lexicon size",
                    "## Degrees of freedom"):
        assert heading in text


def test_cli_refuses_an_unregistered_protocol(capsys):
    assert tier1.main(["--lexicon", "hebrew-strong-verbs", "--protocol", "H-A5-99"]) == 2
    assert "REFUSED" in capsys.readouterr().err
