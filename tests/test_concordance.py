"""Siglum parsing, concordance clustering and inclusion tiers (A1.6).

Parsing fixtures are hand-checked: each input is an ID exactly as a source
writes it (source named), and the expected key follows GORILA's siglum.
"""
from pathlib import Path

import pytest

from aegean.corpus import concordance, inclusion, siglum
from aegean.corpus.concordance import DocCluster, SourceRecord

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("raw,key,side", [
    ("HT13", "HT 13", None),  # lineara.xyz
    ("HT 13", "HT 13", None),  # SigLA / Younger
    ("HT122a", "HT 122", "a"),  # lineara.xyz side
    ("HT Wa 1019α", "HT Wa 1019", "alpha"),  # SigLA nodule face
    ("GO Wc 3 latus", "GO Wc 3", "latus"),  # SigLA roundel edge
    ("KN Zb <27>", "KN Zb <27>", None),  # GORILA: reported, not seen
    ("HTWa1845+1733", "HT Wa 1845+1733", None),  # join
    ("HT 113 ter", "HT 113ter", None),
    ("LA Zb 1 (bis)", "LA Zb 1bis", None),  # Younger
    ("HT 154Ja", "HT 154J", "a"),  # SigLA fragment J, side a
    ("HT154ja", "HT 154J", "a"),  # lineara.xyz writes the same lowercase
    ("HT 154A", "HT 154A", None),  # fragment letter stays in the key
    ("KO(?)Zf2", "KO Zf 2", None),
    ("HT Wa <1021bis>", "HT Wa <1021>bis", None),
])
def test_parse(raw, key, side):
    p = siglum.parse(raw)
    assert (p.key, p.side) == (key, side)


def test_parse_flags_and_failures():
    assert "site_uncertain" in siglum.parse("PH(?) 31").flags
    assert "id_uncertain" in siglum.parse("MOZb2?").flags
    assert siglum.parse("THEfr.1") is None  # irregular: handled by aliases.tsv
    assert siglum.parse("HT 42+59").components == ("HT 42", "HT 59")
    assert siglum.parse("HT Wa <1021bis>").match_key == siglum.parse("HTWa1021bis").match_key


def test_aliases_table_is_well_formed():
    a = concordance.load_aliases()
    assert a[("lineara.xyz", "THEfr.1")] == a[("younger", "THE small tablet fragment 1")]
    assert all(conf in ("high", "medium", "unresolved") for _, conf in a.values())


def cluster(records, series=None):
    return DocCluster("X 1", [], "X", series, *concordance.SERIES_SUPPORT[series], False, False, [], records)


def test_tiers():
    r = lambda src, signs, nums=0: SourceRecord(src, "X1", None, signs=signs, numerals=nums)
    assert inclusion.tier(cluster([r("sigla", 2)])) == "T1"
    assert inclusion.tier(cluster([r("lineara.xyz", 1, 1)])) == "T1"  # logogram + numeral
    assert inclusion.tier(cluster([r("lineara.xyz", 1)], "Wa")) == "T2"  # single-sign nodule
    assert inclusion.tier(cluster([r("lineara.xyz", 0, 3)])) == "T3"  # numerals only
    # the best source decides; sides of one source are summed
    assert inclusion.tier(cluster([r("sigla", 0), r("younger", 1), r("younger", 1)])) == "T1"


def test_decisions_record_every_reason():
    c = cluster([SourceRecord("lineara.xyz", "X1", None, signs=1)], "Wa")
    c.lost = True
    d = inclusion.decide(c)
    assert d.listed and not d.analysis_default
    assert d.reasons == ["R3/R4 tier T2", "R9 lost (<n>)"]
    d = inclusion.decide(c, inclusion.Rules(analysis_tiers=("T1", "T2"), analysis_lost=True))
    assert d.analysis_default


def test_real_concordance_if_inputs_present():
    if not all(p.exists() for p in concordance.INPUTS.values()):
        pytest.skip("lineara.xyz / Younger inputs not present (fetched or downloaded locally)")
    pytest.importorskip("pdfplumber")
    clusters, unmatched = concordance.build()
    assert not unmatched
    by = {c.key: c for c in clusters}
    assert len(clusters) == 1619
    assert by["HT 13"].sources == ["lineara.xyz", "sigla"]  # Younger has no HT
    assert sorted(by["KH Wc 2059"].aliases) == ["KH Wc 2059+2091+2092", "KH Wc 2059+frr",
                                                "KH Wc 2091", "KH Wc 2092"]
    assert by["HT 122"].records and {r.side for r in by["HT 122"].records} >= {"a", "b"}
    assert inclusion.summarise(clusters)["analysis_default"] == 568
