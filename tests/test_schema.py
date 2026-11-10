"""Schema, sign IDs and source adapters (A1.7).

Expected values for real documents come from the rendered sources checked
earlier: SigLA HT 13 (sigla.phis.me, index-N pages; tests/test_corpus_sigla.py)
and Younger ZA 8 (PDF p. 121; tests/test_corpus_younger.py). The lineara.xyz
HT13 first word is checked against SigLA's (the same signs, KA-U-DE-TA).
"""
from pathlib import Path

import pytest

from aegean.corpus import schema as sc
from aegean.corpus import sigla, witnesses as W

REPO = Path(__file__).resolve().parents[1]
SIGLA = REPO / "data/raw/sigla/0c4ef69f5de4/database.js"
LINEARA = REPO / "data/raw/lineara.xyz/9c81beba669a/LinearAInscriptions.js"
YOUNGER = REPO / "data/raw/younger/academia-2024/Linear_A_Texts_in_phonetic_transcription.pdf"


@pytest.mark.parametrize("name,expected", [
    ("LINEAR A SIGN AB081", "AB081"),
    ("LINEAR A SIGN AB131A", "AB131a"),
    ("LINEAR A SIGN A131C", "AB131c"),  # Unicode puts this AB variant in the A series
    ("LINEAR A SIGN A028B", "AB028b"),
    ("LINEAR A SIGN A400-VAS", "A400"),
    ("LINEAR A SIGN A709-2 L2", "A709-2"),
    ("LINEAR A SIGN A732 JE", "A732"),
    ("LINEAR A SIGN AB021F", "AB021f"),
])
def test_from_unicode_name(name, expected):
    assert sc.from_unicode_name(name) == expected


@pytest.mark.parametrize("sid,expected", [
    ("AB77", "AB077"), ("AB131a", "AB131a"), ("AAF707", "A707"), ("AAF709-2", "A709-2"),
    ("A506bis", "A506bis"), ("AB21f", "AB021f"), ("AAP800", "SigLA:AAP800"), ("AAZ1000", "SigLA:AAZ1000"),
])
def test_from_sigla_id(sid, expected):
    assert sc.from_sigla_id(sid) == expected


def test_ligatures_keep_both_forms():
    t = W._fraction_token("JE")
    assert (t.sign_id, t.components) == ("A732", ["A707", "A704"])
    assert W._fraction_token("DD").components == ["A703", "A703"]
    assert W._fraction_token("J").components == [] and W._fraction_token("J").sign_id == "A707"
    assert sc.unicode_codepoint("A732") == "U+10755" and sc.unicode_codepoint("A718") is None


def test_base_id():
    assert sc.base_id("AB131a") == "AB131" and sc.base_id("A709-2") == "A709" and sc.base_id(None) is None


def test_validate_catches_errors():
    bad = sc.Witness("x", "X 1", "v", None, "L9", [sc.Line(0, None, "weird", items=[
        sc.Item("numeral"), sc.Item("word", [sc.Token("?", "XYZ", unidentified=True)])])])
    errs = sc.validate(bad)
    assert any("bad layer" in e for e in errs) and any("ref_kind" in e for e in errs)
    assert any("numeral without value" in e for e in errs) and any("non-canonical" in e for e in errs)
    assert any("unidentified token with a sign_id" in e for e in errs)


def test_sigla_witness_ht13():
    signs = {s.sign_id: s for s in sigla.load_signs(SIGLA)}
    d = {x.id: x for x in sigla.load_documents(SIGLA)}["HT 13"]
    w = W.from_sigla(d, signs)
    assert not sc.validate(w)
    items = w.lines[0].items
    assert w.lines[0].ref_kind == "none" and w.layer == "L0"
    assert (items[0].kind, [t.sign_id for t in items[0].tokens]) == ("word", ["AB077", "AB010", "AB045", "AB059"])
    assert (items[1].kind, items[1].tokens[0].sign_id) == ("logogram", "AB131a")
    assert (items[2].kind, items[2].tokens[0].sign_id) == ("transaction", "AB004")
    assert any(it.kind == "fraction" and it.tokens[0].sign_id == "A707" for it in items)
    assert all(t.doubtful is False for t in w.tokens())  # SigLA records sure readings
    assert all(t.restored is None and t.stacked is None for t in w.tokens())  # SigLA records neither


def test_all_sigla_witnesses_validate():
    signs = {s.sign_id: s for s in sigla.load_signs(SIGLA)}
    assert all(not sc.validate(W.from_sigla(d, signs)) for d in sigla.load_documents(SIGLA))


def test_lineara_witness_if_present():
    if not LINEARA.exists():
        pytest.skip("lineara.xyz snapshot not fetched (data/raw/lineara.xyz/fetch.py)")
    from aegean.corpus import lineara
    from aegean.corpus.heldout import load_heldout
    docs = {d.id: d for d in lineara.load_documents(LINEARA, load_heldout()["lineara.xyz"])}
    w = W.from_lineara(docs["HT13"])
    assert not sc.validate(w)
    assert [t.sign_id for t in w.lines[0].items[0].tokens] == ["AB077", "AB010", "AB045", "AB059"]
    assert all(t.doubtful is None for t in w.tokens())  # lineara.xyz records no doubt
    je = [t for d in docs.values() for t in W.from_lineara(d).tokens() if t.sign_id == "A732"]
    assert je and all(t.components == ["A707", "A704"] for t in je)


def test_younger_witness_za8_if_present():
    pytest.importorskip("pdfplumber")
    if not YOUNGER.exists():
        pytest.skip("Younger PDF not downloaded (data/raw/younger/README.md)")
    from aegean.corpus import younger
    d = {x.id: x for x in younger.load_documents(YOUNGER)}["ZA 8"]
    w = W.from_younger(d)
    assert not sc.validate(w) and w.layer == "L0+L1"
    by_ref = {}
    for ln in w.lines:
        by_ref.setdefault(ln.ref, []).append(ln)
    two = by_ref[".2"][0].items
    assert [t.l1_value for t in two[0].tokens] == ["KU", "TU", "KO", "RE"] and all(t.sign_id is None for t in two[0].tokens)
    assert [t.sign_id for t in two[1].tokens] == ["A703", "A703"]  # "D D", separate signs in Younger
    num = [it for it in by_ref[".2-3"][0].items if it.kind == "numeral"][0]
    assert (num.raw, num.numeral_value, num.right_break) == ("1[ ]", 1, "[")
