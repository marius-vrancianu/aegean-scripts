"""Layers L0/L1 (A1.8). Value tables are checked against their stated sources:
Unicode Linear B names (unicodedata), SigLA's sign table, Younger's introduction."""
from pathlib import Path

import pytest

from aegean.corpus import layers as L
from aegean.corpus import schema as sc
from aegean.corpus import sigla

REPO = Path(__file__).resolve().parents[1]
SIGLA = REPO / "data/raw/sigla/0c4ef69f5de4/database.js"


@pytest.mark.parametrize("sid,l1", [
    ("AB081", "KU"), ("AB067", "KI"), ("AB002", "RO"),  # KU-RO, KI-RO
    ("AB029", "PU2"), ("AB066", "TA2"), ("AB076", "RA2"),
    ("AB056", "*56"), ("AB079", "*79"), ("AB022", "*22"),  # Unicode gives no value: number kept
    ("A301", "*301"), ("AB131a", "*131a"),  # Linear A-only sign; variant of a logogram
    ("A707", "J"), ("A732", "JE"), ("A717", "DD"), ("SigLA:AAP800", None), (None, None),
])
def test_l1_of(sid, l1):
    assert L.l1_of(sid) == l1


@pytest.mark.parametrize("value,sid", [
    ("KU", "AB081"), ("RO", "AB002"), ("*301", "A301"), ("*411VASb", "A411b"),
    ("PA3", "AB056"), ("PU3", "A314"), ("ZU", "AB079"), ("AI", "AB043"),
    ("VINa", "AB131a"), ("OVISf", "AB021f"), ("OLE", "A302"), ("QIf", "AB021f"), ("J", "A707"),
    ("vest.", None), ("a:", None),
])
def test_younger_value_to_l0(value, sid):
    assert L.younger_value_to_l0(value)[0] == sid


def test_younger_logogram_cells():
    assert L.younger_logogram_to_l0("GRA+PA {*574}", {})[:2] == ("A574", [])
    assert L.younger_logogram_to_l0("OVISf", {})[0] == "AB021f"
    assert L.younger_logogram_to_l0("*301+*311", {"*301+*311": "A999"})[0] == "A999"
    sid, comps, rule = L.younger_logogram_to_l0("*301+*311", {})
    assert sid is None and comps == ["A301", "A311"] and rule == "components_only"


def test_unicode_table_is_the_source():
    # The table is read from unicodedata, not typed in: spot-check its size and a few entries.
    assert len(L.LB_VALUES) == 74
    assert L.LB_VALUES["AB008"] == "A" and L.LB_VALUES["AB043"] == "A3" and "AB056" not in L.LB_VALUES


def test_sigla_value_subscripts_fixed():
    signs = {s.sign_id: s for s in sigla.load_signs(SIGLA)}
    assert signs["AB29"].conventional_values == ["pu2"]
    assert signs["AB66"].conventional_values == ["ta2"] and signs["AB77"].conventional_values == ["ka"]


def test_series_follows_number():
    assert sc.from_sigla_id("AB302") == "A302"  # SigLA's OLE
    assert sc.canonical_id("A", 28, "b") == "AB028b"


def test_apply_younger_like_witness():
    w = sc.Witness("younger", "X 1", "v", None, "L0+L1", [sc.Line(0, ".1", "physical", items=[
        sc.Item("word", [sc.Token("KU", None, l1_value="KU"), sc.Token("RO", None, l1_value="RO")]),
        sc.Item("logogram", [sc.Token("VINa", None, "logogram", l1_value="VINa")]),
    ])])
    out = L.apply(w)
    toks = list(out.tokens())
    assert [t.sign_id for t in toks] == ["AB081", "AB002", "AB131a"]
    assert [t.l1 for t in toks] == ["KU", "RO", "*131a"]
    assert all(t.sign_id is None for t in w.tokens())  # the input witness is not modified


def test_build_if_inputs_present():
    from aegean.corpus import concordance
    if not all(p.exists() for p in concordance.INPUTS.values()):
        pytest.skip("lineara.xyz / Younger inputs not present")
    pytest.importorskip("pdfplumber")
    from aegean.corpus import build_layers
    _, val = build_layers.all_witnesses()
    assert val["documents_paired"] == 335
    assert val["agree"] / val["aligned"] > 0.98
    for v, sid in (("PA3", "AB056"), ("ZU", "AB079"), ("PU3", "A314")):
        assert set(val["per_value"][v]) == {sid}  # every aligned occurrence agrees with SigLA
