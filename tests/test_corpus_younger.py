"""Tests for the Younger reader.

Unit tests build synthetic characters and run everywhere. File tests need the
manually downloaded PDF (not committed; data/raw/younger/README.md) and
pdfplumber; they skip otherwise. Every expected value in the file tests was
read off the rendered PDF page named next to it (page images checked
2026-11-10).
"""
from pathlib import Path

import pytest

from aegean.corpus import younger as y

REPO = Path(__file__).resolve().parents[1]
PDF = REPO / "data/raw/younger/academia-2024/Linear_A_Texts_in_phonetic_transcription.pdf"


def word(text, underlined=(), green=(), x0=100.0):
    chars = [y.Char(ch, x0 + 5 * i, x0 + 5 * i + 4, 100, 110, False, False,
                    y.GREEN if i in green else y.BLACK, 12.0, i in underlined)
             for i, ch in enumerate(text)]
    return y.Word(chars)


def signs(g):
    return [(s.value, s.break_before, s.break_after) for s in g.signs]


# --- unit tests ------------------------------------------------------------------

def test_breaks_with_and_without_lost_part():
    assert signs(y.parse_group(word("]-NU-TI"))) == [("NU", "]-", ""), ("TI", "", "")]
    assert signs(y.parse_group(word("]TA-PI"))) == [("TA", "]", ""), ("PI", "", "")]
    assert signs(y.parse_group(word("ZA-["))) == [("ZA", "", "-[")]
    assert signs(y.parse_group(word("A-RA["))) == [("A", "", ""), ("RA", "", "[")]


def test_underline_marks_single_sign_doubtful():
    g = y.parse_group(word("]RO-SI-RA[", underlined={1, 2}))  # ZA 9.3-4: RO underlined
    assert [s.doubtful for s in g.signs] == [True, False, False]


def test_unidentified_erased_restored_conjectural():
    g = y.parse_group(word("A-TA-NA-[•]"))
    assert [(s.value, s.unidentified) for s in g.signs][-1] == ("•", True)
    assert [s.value for s in g.signs] == ["A", "TA", "NA", "•"]
    assert y.parse_group(word("•-MA-JU")).signs[0].unidentified
    assert all(s.erased for s in y.parse_group(word("[[NA]]")).signs)
    assert [s.restored for s in y.parse_group(word("KU-<RO>")).signs] == [False, True]
    assert [s.conjectural for s in y.parse_group(word("JU-MA", green={0, 1})).signs] == [True, False]


def test_subscript_values_stay_whole():
    assert [s.value for s in y.parse_group(word("RA2-RO-RE")).signs] == ["RA2", "RO", "RE"]
    assert [s.value for s in y.parse_group(word("*301-U-JA")).signs] == ["*301", "U", "JA"]


def test_lacuna_dots_are_not_dividers():
    ws = [word("I-PI-NA-MA"), word("["), *[word("•") for _ in range(6)], word("]I-KU")]
    gs = y._statement_groups(ws)
    assert [g.lacuna_dots for g in gs] == [None, 6, None]
    assert gs[2].signs[0].break_before == "]"
    ws = [word("TA["), word("•"), word("•"), word("•"), word("]-QA"), word("•")]
    gs = y._statement_groups(ws)
    assert [g.lacuna_dots for g in gs] == [None, 3, None] and gs[2].divider_after


def test_divider_between_words():
    gs = y._statement_groups([word("A-DA-KI-SI-KA"), word("•"), word("A-RA-U-DA"), word("•")])
    assert [g.divider_after for g in gs] == [True, True]


def test_normalise_id():
    assert y.normalise_id("PH(?) 31") == ("PH 31", [], ["site_uncertain"])
    assert y.normalise_id("KH Wa 1003, 1004") == ("KH Wa 1003", ["KH Wa 1004"], [])
    assert y.normalise_id("KH Wa 1006-1008") == ("KH Wa 1006", ["KH Wa 1007", "KH Wa 1008"], ["range"])
    assert y.normalise_id("ZA 10")[2] == []
    assert "irregular_siglum" in y.normalise_id("THE small tablet fragment 1")[2]


def test_prose_lines():
    assert y._is_prose([word("CMS"), word("II"), word("5,"), word("weave"), word("pattern")])
    assert not y._is_prose([word("VINa+TE"), word("{*588}")])
    assert not y._is_prose([word("OVISf")])


# --- file tests (need the manual download and pdfplumber) ---------------------------

@pytest.fixture(scope="module")
def docs():
    pytest.importorskip("pdfplumber")
    if not PDF.exists():
        pytest.skip("Younger PDF not downloaded (data/raw/younger/README.md)")
    return {d.id: d for d in y.load_documents(PDF)}


def row(d, ref, k=0):
    return [r for r in d.rows if r.ref == ref][k]


def test_file_counts(docs):
    assert len(docs) >= 500
    assert "KH 100" in docs  # heading printed in blue (p. 43)


def test_za8(docs):
    # p. 121: ZA 8, page tablet; ".1 A-TA-RE • FIC J"; ".2 KU-TU-KO-RE D D";
    # ".2-3 A-RI-NI-TA 1[ ] B B"; ".4 MA-KA-I-SE 2 E J"; ".6 KA-I-RO 4 B B". Numbers bold.
    d = docs["ZA 8"]
    assert d.layout == "table" and d.annotations == ["Schoep 2002, type III (single commodity)", "ZA Scribe 2"]
    r = row(d, ".1", 1)
    assert (r.logogram, r.number, r.fraction) == ("FIC", None, "J") and r.statement[0].divider_after
    assert row(d, ".2").fraction == "D D"
    assert (row(d, ".2-3").number, row(d, ".2-3").fraction) == ("1[ ]", "B B")
    assert (row(d, ".4").number, row(d, ".4").fraction) == ("2", "E J")
    assert (row(d, ".6").number, row(d, ".6").fraction) == ("4", "B B")
    assert any("59/60" in n for n in d.notes)  # red commentary


def test_za9_doubt_and_breaks(docs):
    # p. 121: ".2 ]-RA OVIS+SI {*512} 5" (5 underlined); ".3-4 ]RO-SI-RA[ ]" (RO underlined),
    # OVIS underlined, 4 underlined; ".4-5 A-TA-NA-[•] ... 2" (2 underlined); ".5 [•]-MA-JU OVISf 2".
    d = docs["ZA 9"]
    r = row(d, ".2")
    assert signs(r.statement[0]) == [("RA", "]-", "")] and r.number == "5" and r.number_doubtful
    r = row(d, ".3-4")
    assert [s.doubtful for s in r.statement[0].signs] == [True, False, False]
    assert r.logogram_doubtful and r.number_doubtful and r.number == "4"
    assert row(d, ".4-5").statement[0].signs[-1].unidentified
    assert row(d, ".5").statement[0].signs[0].unidentified and not row(d, ".5").number_doubtful


def test_kh5(docs):
    # p. 15: ".3 WI-NA-DU • *301-NA •" (301 underlined); ".3-4 KU-PA-ZU *303+[ ] 3[ A"
    # (*303 and 3 underlined); ".4 FIC 2 J B".
    d = docs["KH 5"]
    assert row(d, ".3").logogram_doubtful
    r = row(d, ".3-4")
    assert (r.logogram, r.number, r.fraction) == ("*303+[ ]", "3[", "A") and r.number_doubtful
    r = row(d, ".4")
    assert (r.logogram, r.number, r.fraction) == ("FIC", "2", "J B")


def test_kh3_ruling_and_vacat(docs):
    # p. 15: "supra mutila", ".1 ]NU 1" (both underlined), ruled line, ".2 vacat".
    d = docs["KH 3"]
    r = row(d, ".1")
    assert (r.logogram, r.number) == ("]NU", "1") and r.logogram_doubtful and r.number_doubtful
    assert any(o.startswith(("_", "—")) for x in d.rows for o in x.other)
    assert row(d, ".2").other == ["vacat"]


def test_ap_za2_text_with_lacunae(docs):
    # p. 1: ".1: ]NA-SI • I-PI-NA-MA [ • • • • • • ]I-KU-PA3-NA-TU-NA-TE [" (]I underlined);
    # ".2: ]PI-MI-NA-TE • I-NA-JA-RE-TA[ • • • ]-QA •" (TA underlined).
    d = docs["AP Za 2"]
    assert d.layout == "text"
    g = row(d, ".1").statement
    assert [x.lacuna_dots for x in g if x.lacuna_dots] == [6]
    kupa = [x for x in g if x.signs and x.signs[0].value == "I" and x.signs[0].break_before == "]"][0]
    assert kupa.signs[0].doubtful and [s.value for s in kupa.signs][2] == "PA3"
    g = row(d, ".2").statement
    assert [x.lacuna_dots for x in g if x.lacuna_dots] == [3]
    assert g[1].signs[-1].value == "TA" and g[1].signs[-1].doubtful and g[1].signs[-1].break_after == "["


def test_za10_subscript(docs):
    # p. 122: "b.5 RA2-RO-RE 2" (subscript 2 printed smaller).
    r = row(docs["ZA 10"], "b.5")
    assert [s.value for s in r.statement[0].signs] == ["RA2", "RO", "RE"] and r.number == "2"


def test_ph31_reconstruction_kept_apart(docs):
    # pp. 95-98: after the commentary, Younger reprints PH 31 with switched sides and green fills.
    d = docs["PH 31"]
    assert "site_uncertain" in d.flags  # printed "PH(?) 31"
    assert d.rows and len(d.commentary_rows) > 10
    green = [s for r in d.commentary_rows for g in r.statement for s in g.signs if s.conjectural]
    assert green  # e.g. "TU-[JU-MA" with JU-MA in green (p. 98)
    assert not any(s.conjectural for r in d.rows for g in r.statement for s in g.signs)
