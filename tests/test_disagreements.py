"""Comparison primitives of the A1.9 disagreement report, on synthetic witnesses."""
import pytest

from aegean.corpus import disagreements as D
from aegean.corpus import schema as sc


def witness(source, groups, numerals=(), fractions=()):
    items = [sc.Item("word", [sc.Token(s, s) for s in g]) for g in groups]
    items += [sc.Item("numeral", numeral_value=n, raw=str(n)) for n in numerals]
    items += [sc.Item("fraction", [sc.Token(f, f, "fraction", list(sc.FRACTION_LIGATURES.get(f, ())))])
              for f in fractions]
    return sc.Witness(source, "X 1", "v", None, "L0", [sc.Line(0, None, "none", items=items)])


def test_sign_alignment_counts():
    a = D.words([witness("a", [["AB081", "AB002"], ["AB067", "AB002"]])])
    b = D.words([witness("b", [["AB081", "AB002"], ["AB067", "AB003"]])])
    r = D.compare_signs(a, b)
    assert r["counts"]["agree"] == 3 and r["counts"]["substitution"] == 1
    assert r["substitutions"] == [("AB002", "AB003")]


def test_variant_only_counts_as_agreement_of_base():
    r = D.compare_signs(D.words([witness("a", [["AB131a"]])]), D.words([witness("b", [["AB131b"]])]))
    assert r["counts"]["agree"] == 1 and r["counts"]["variant_only"] == 1


def test_word_division():
    a = D.words([witness("a", [["AB081", "AB002"], ["AB067", "AB002"]])])
    b = D.words([witness("b", [["AB081", "AB002", "AB067", "AB002"]])])
    c = D.compare_division(a, b)
    assert c["boundary_only_a"] == 1 and c["boundary_only_b"] == 0


def test_fraction_ligatures_expand():
    la, nla = D.fractions([witness("a", [], fractions=["A732"])])  # JE as one codepoint
    lb, nlb = D.fractions([witness("b", [], fractions=["A707", "A704"])])  # J, E separately
    assert la == lb == ["J", "E"] and (nla, nlb) == (1, 0)


def test_numerals_in_order():
    assert D.numerals([witness("a", [], numerals=[15, 120])]) == [15, 120]


def test_fractions_are_not_signs():
    w = witness("a", [["AB081"]], fractions=["A707"])
    assert [x["base"] for x in D.words([w])] == [("AB081",)]


def test_unicode_man_sign_alias():
    assert sc.from_unicode_name("LINEAR A SIGN A100-102") == "AB100"
