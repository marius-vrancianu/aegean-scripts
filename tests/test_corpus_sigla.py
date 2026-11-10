"""Fixture tests for the SigLA reader on the committed snapshot 0c4ef69f.

Every expected value below was read off the rendered site (sigla.phis.me) on
2026-11-10. The page each value was checked on is named next to it. The site
numbers attestations from #1, so attestation index i is shown as "#i+1".
"""
from pathlib import Path

import pytest

from aegean.corpus import sigla

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "data/raw/sigla/0c4ef69f5de4/database.js"


@pytest.fixture(scope="module")
def docs():
    return {d.id: d for d in sigla.load_documents(SNAPSHOT)}


@pytest.fixture(scope="module")
def signs():
    return {s.sign_id: s for s in sigla.load_signs(SNAPSHOT)}


def test_snapshot_hash():
    import hashlib
    sums = (REPO / "data/raw/sigla/SHA256SUMS").read_text().split()
    assert hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest() == sums[sums.index("0c4ef69f5de4/database.js") - 1]


def test_counts(docs, signs):
    # Header/self-consistency counts of this snapshot (not a claim about the corpus).
    assert len(docs) == 827
    assert sum(len(d.attestations) for d in docs.values()) == 5184
    assert sum(len(d.words) for d in docs.values()) == 1417
    assert len(signs) == 388


def test_ht13_document(docs):
    # document/HT 13/index.html: "Tablet found at Haghia Triada (6.1 cm × 10.5 cm × 0.8 cm)",
    # "Period: LM IB", "27 signs / 8 words"; SVG viewBox 0 0 1367 2253.
    d = docs["HT 13"]
    assert (d.support, d.site, d.dimensions_cm, d.period) == ("Tablet", "Haghia Triada", (6.1, 10.5, 0.8), "LM IB")
    assert d.drawing_size == (1367, 2253)
    assert (len(d.attestations), len(d.words)) == (27, 8)


def test_ht13_signs_and_classes(docs):
    a = docs["HT 13"].attestations
    # index-1.html "#2: u Syllabogram"; index-4.html "#5: AB131a/VIN Logogram";
    # index-5.html "#6: AB04 Transaction sign"; index-8.html "#9: J (fraction) Fraction";
    # index-6.html "#7: re"; index-9.html "#10: te"; index-10.html "#11: tu".
    assert (a[1].sign_id, a[1].sign_class) == ("AB10", "syllabogram")
    assert (a[4].sign_id, a[4].sign_class) == ("AB131a", "logogram")
    assert (a[5].sign_id, a[5].sign_class) == ("AB4", "transaction")
    assert (a[8].sign_id, a[8].sign_class) == ("AAF707", "fraction")
    assert [a[i].sign_id for i in (6, 9, 10)] == ["AB27", "AB4", "AB69"]  # re, te, tu
    # index-word.html: first word box spans attestations #1-#4 ("ka-u-de-ta" in word-0).
    assert docs["HT 13"].words[0].attestations == [0, 1, 2, 3]
    assert a[2].word == 0 and a[2].index_in_word == 2
    assert a[4].word is None
    # HT 13 word-0 first box: x=169 y=88 w=221 h=212 (index-word.html <rect>).
    assert a[0].bbox == (169, 88, 221, 212)


def test_erasure_unknown_punctuation(docs):
    # HT 101 index-11.html "#12: A610 Erasure (Unknown)";
    # index-12.html "#13: num Erasure (Punctuation)".
    x, y = docs["HT 101"].attestations[11], docs["HT 101"].attestations[12]
    assert (x.sign_id, x.erased, x.sign_class, x.class_uncertain) == ("A610", True, "unknown", False)
    assert (y.sign_id, y.erased, y.sign_class) == ("AAP800", True, "punctuation")
    # HT 10a index-12.html "#13: [?] Erasure (Unknown?)".
    z = docs["HT 10a"].attestations[12]
    assert (z.sign_status, z.sign_id, z.erased, z.sign_class, z.class_uncertain) == (
        "unidentified", None, True, "unknown", True)


def test_unidentified_unclassified(docs):
    # ARKH 1a index-13.html "#14: [?] Syllabogram"; HT 28b index-26.html "#27: [unclassified] Logogram".
    a = docs["ARKH 1a"].attestations[13]
    assert (a.sign_status, a.sign_class, a.reading_sure) == ("unidentified", "syllabogram", None)
    b = docs["HT 28b"].attestations[26]
    assert (b.sign_status, b.sign_class) == ("unclassified", "logogram")


def test_sure_and_unsure_readings(docs):
    # ARKH 4b index-10.html: <span class="unsure-reading">za</span>;
    # index-9.html: <span class="sure-reading">ro</span>.
    assert docs["ARKH 4b"].attestations[10].sign_id == "AB17"
    assert docs["ARKH 4b"].attestations[10].reading_sure is False
    assert docs["ARKH 4b"].attestations[9].sign_id == "AB2"
    assert docs["ARKH 4b"].attestations[9].reading_sure is True
    # HT 102 index-8.html: "#9: F (fraction)" as unsure-reading.
    f = docs["HT 102"].attestations[8]
    assert (f.sign_id, f.sign_class, f.reading_sure) == ("AAF705", "fraction", False)


def test_hidden_attestation(docs):
    # HT 22 index.html: "3 signs / 1 words", but only #1 and #2 are drawn; index-2.html is empty.
    d = docs["HT 22"]
    assert len(d.attestations) == 3
    assert [a.hidden for a in d.attestations] == [False, False, True]
    assert d.dimensions_cm == (3.4, 3.0, 0.6)


def test_word_edges(docs):
    # Word views: ARKH 1a index-word-0 "]ta-pi", index-word-4 "a-pa-[?][";
    # ARKH 3a index-word-0 "]-ka-ne"; ARKH 2 index-word-5 "ru-mi-[".
    w = lambda d, i: (docs[d].words[i].left_edge, docs[d].words[i].right_edge)
    assert w("ARKH 1a", 0) == (2, 0)
    assert w("ARKH 1a", 4) == (0, 2)
    assert w("ARKH 3a", 0) == (1, 0)
    assert w("ARKH 2", 5) == (0, 1)
    assert w("HT 13", 0) == (0, 0)  # "ka-u-de-ta"
    assert sigla.EDGE_RENDERING[1] == ("]-", "-[") and sigla.EDGE_RENDERING[2] == ("]", "[")


def test_seal_metadata(docs):
    # Decoded seal record of GO Wc 1a: CMS II,6 no. 159, motif "bull".
    d = docs["GO Wc 1a"]
    assert (d.seal_cms, d.seal_motif) == ("CMS II,6 no. 159", "bull")


def test_metadata_id_mismatches_are_kept(docs):
    # Source-internal inconsistency, recorded for A1.9 rather than resolved.
    assert docs["KH 87"].metadata_id == "KH 97"
    assert docs["PH Wa 52"].metadata_id == "PE Wa 52"
    assert docs["HT 13"].metadata_id is None
    assert sum(1 for d in docs.values() if d.metadata_id) == 7


def test_sign_table(signs):
    # Sign table: J = AAF707; DD and DDDD are single signs; no JE ligature sign exists.
    assert signs["AAF707"].name == "J"
    assert signs["AAF717"].name == "DD" and signs["AAF718"].name == "DDDD"
    assert not any(s.name == "JE" for s in signs.values())
    assert signs["AB77"].conventional_values == ["ka"]  # L1, kept out of attestations
    # Compositions match the GORILA-style text in the same record.
    assert signs["A501"].composition_text == "*01 || *02"
    assert signs["A501"].composition == {"op": "||", "parts": ["AB1", "AB2"]}
    assert signs["A588"].composition_text == "*131a+{*04}"
    assert signs["A588"].composition == {"op": "+{}", "parts": ["AB131a", "AB4"]}


def test_attestations_carry_no_l1_values(docs):
    fields = set(sigla.Attestation.__dataclass_fields__)
    assert not fields & {"conventional_values", "value", "reading"}


def test_heldout_filter():
    keys = sigla.heldout_keys({"lineara.xyz": {"HT13", "ZA10a"}})
    assert sigla.is_heldout("HT 13", keys)
    assert sigla.is_heldout("ZA 10a", keys) and sigla.is_heldout("ZA 10", keys)
    assert not sigla.is_heldout("HT 130", keys)
    # The real list removes nothing from this snapshot (no held-out record in it).
    assert len(sigla.load_documents(SNAPSHOT)) == 827


def test_heldout_ids_are_dropped_before_interpretation():
    docs = sigla.load_documents(SNAPSHOT, heldout={"test": {"HT13"}})
    assert "HT 13" not in {d.id for d in docs} and len(docs) == 826
