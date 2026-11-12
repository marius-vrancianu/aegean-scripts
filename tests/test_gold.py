"""Gold set (A8.1): detection rules on synthetic witnesses, and consistency of the committed files."""
import hashlib
import json

from aegean.roles import gold


def tok(sign, bbox=None, components=()):
    return {"sign_id": sign, "bbox": bbox, "components": list(components)}


def item(kind, toks):
    return {"kind": kind, "tokens": toks}


def sigla(doc, items):
    return {"doc_key": doc, "source": "sigla", "lines": [{"items": items}]}


def lineara(doc, items):
    return {"doc_key": doc, "source": "lineara.xyz", "lines": [{"items": items}]}


BIG = [item("word", [tok("AB001", (0, 0, 100, 300)), tok("AB002", (120, 0, 100, 300)), tok("AB003", (240, 0, 100, 300))])]
VESSEL = item("logogram", [tok("A402", (500, 400, 200, 250))])
SMALL_OVER = item("word", [tok("AB058", (500, 300, 90, 130)), tok("AB050", (600, 310, 90, 130))])  # reaches y=440 > 400
NORMAL_OVER = item("word", [tok("AB058", (500, 130, 90, 300)), tok("AB050", (600, 130, 90, 300))])
FAR_ABOVE = item("word", [tok("AB058", (500, 100, 90, 130)), tok("AB050", (600, 100, 90, 130))])  # ends at 230 < 400
BESIDE = item("word", [tok("AB058", (900, 300, 90, 130)), tok("AB050", (1000, 300, 90, 130))])


def verdicts(items):
    return [(c.get("group_l1"), c["verdict"]) for c in gold.sigla_candidates(sigla("XX 1", BIG + items))]


def test_vessel_series():
    assert gold.is_vessel("A400") and gold.is_vessel("A418") and gold.is_vessel("A411a")
    assert not gold.is_vessel("A419") and not gold.is_vessel("AB040") and not gold.is_vessel("A302") and not gold.is_vessel(None)


def test_small_group_over_a_vessel_is_a_label():
    assert verdicts([VESSEL, SMALL_OVER]) == [("SU-PU", "label")]


def test_normal_size_far_or_beside_is_not():
    assert verdicts([VESSEL, NORMAL_OVER]) == [("SU-PU", "not_gold")]
    assert verdicts([VESSEL, FAR_ABOVE]) == [(None, "not_gold")]
    assert verdicts([VESSEL, BESIDE]) == [(None, "not_gold")]


def test_ligature_is_an_adjunct_not_a_label():
    c = gold.sigla_candidates(sigla("XX 1", BIG + [item("logogram", [tok("A651", (500, 400, 200, 250), ("A401", "AB026"))])]))
    assert c[0]["verdict"] == "not_gold" and "adjunct" in c[0]["reason"] and c[0]["components"] == "A401+AB026"


def test_lineara_encoding():
    w = lineara("XX 1", [item("word", [tok("A415"), tok("AB058"), tok("AB050")]), item("word", [tok("A402")]),
                         item("word", [tok("AB001"), tok("AB002")])])
    c = gold.lineara_candidates(w)
    assert [(x.get("group_l1"), x["verdict"]) for x in c] == [("SU-PU", "label"), (None, "not_gold")]


def test_grades_need_both_layout_sources_to_agree():
    s = sigla("XX 1", BIG + [VESSEL, SMALL_OVER])
    both, _ = gold.labelled_pictures([s, lineara("XX 1", [item("word", [tok("A402"), tok("AB058"), tok("AB050")])])])
    assert [(g["item_l1"], g["grade"], g["role"]) for g in both] == [("SU-PU", "A", "vessel_designation")]
    one, _ = gold.labelled_pictures([s])
    assert [g["grade"] for g in one] == ["B"]
    conflict, cands = gold.labelled_pictures([s, lineara("XX 1", [item("word", [tok("A402")])])])
    assert conflict == [] and any("not shown by lineara.xyz" in c["reason"] for c in cands)


def test_literature_items_exact_match_only(tmp_path):
    p = tmp_path / "lit.tsv"
    p.write_text("item_l1\trole\treferent\tgrade\tsurvey_confidence\tsources\tsource_check\tnote\n"
                 "KU-RO\ttotal_marker\ttotal\tA\tnear-certain\tx\ty\t\n"
                 "PA-I-TO\tplace\tPhaistos\tA\thigh\tx\ty\t\n", encoding="utf-8")
    ws = [sigla("XX 1", [item("word", [tok("AB081"), tok("AB002")]),
                         item("word", [tok("AB011"), tok("AB005"), tok("AB081"), tok("AB002")])]),
          lineara("XX 2", [item("word", [tok("AB081"), tok("AB002"), tok("A704")])])]  # trailing fraction ignored
    ku, pa = gold.literature_items(ws, p)
    assert ku["signs_l0"] == "AB081 AB002" and ku["n_train_docs"] == 2
    assert ku["train_docs_sigla"] == "XX 1" and ku["train_docs_lineara.xyz"] == "XX 2"
    assert "inside longer sign-groups on 1" in ku["note"]
    assert pa["n_train_docs"] == 0 and "Not attested" in pa["note"]


def test_committed_gold_files_are_consistent():
    m_path = gold.OUT / "MANIFEST.json"
    if not m_path.exists():
        return
    m = json.loads(m_path.read_text(encoding="utf-8"))
    tsv = (gold.OUT / "gold-set.tsv").read_bytes()
    assert hashlib.sha256(tsv).hexdigest() == m["gold_set_sha256"]
    assert hashlib.sha256(gold.INPUT.read_bytes()).hexdigest() == m["literature_input_sha256"]
    assert m["split"] == "train" and tsv.count(b"\n") - 1 == m["counts"]["items"]
