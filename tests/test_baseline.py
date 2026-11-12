"""Baseline statistics (A1.11): hand-checked counts on a synthetic witness."""
import json

from aegean.corpus import baseline


def tok(sign, role=None, doubtful=None, **kw):
    return {"sign_id": sign, "role": role, "doubtful": doubtful, "unidentified": sign is None, **kw}


def item(kind, signs, left=None, right=None):
    return {"kind": kind, "left_break": left, "right_break": right, "tokens": [tok(s) for s in signs]}


W = {"doc_key": "AA 1", "source": "sigla", "period": "LM IB", "lines": [
    {"items": [item("word", ["AB081", "AB002"]),                      # KU-RO, complete
               item("numeral", []),
               item("word", ["AB008", "AB131a", "AB002"]),            # complete; variant merged to AB131
               item("logogram", ["AB131b"]),                          # one-sign group
               item("fraction", ["A707"])]},                          # not a sign-group
    {"items": [item("word", ["AB081", None, "AB002"], left="]"),      # left edge broken, one unidentified
               item("word", ["AB008", "A704", "AB002"]),              # fraction sign removed -> 2 signs
               item("lacuna", [])]}]}


def test_counts_hand_checked():
    k = baseline.counts([W])
    t = k["totals"]
    assert t["sign_groups"] == 5 and t["one_sign_groups"] == 1 and t["multi_sign_groups"] == 4
    assert t["multi_sign_groups_complete"] == 3
    assert t["tokens"] == 11 and t["unidentified_tokens"] == 1
    assert k["sign_frequency"] == {"AB002": 4, "AB081": 2, "AB008": 2, "AB131": 2}
    assert k["position"]["AB081"] == {"initial": 1, "edge_broken": 1}
    assert k["position"]["AB002"] == {"final": 4}
    assert k["position"]["AB131"] == {"medial": 1}
    assert k["group_length"] == {"2": 2, "3": 2} and k["group_length_complete"] == {"2": 2, "3": 1}
    assert t["items_numeral"] == 1 and t["items_fraction"] == 1 and t["items_lacuna"] == 1


def test_headline_hand_checked():
    h = baseline.headline([W])
    assert h["identified_sign_tokens"] == 10 and h["distinct_signs"] == 4 and h["signs_occurring_once"] == 0
    assert h["multi_sign_groups"] == 4 and h["mean_multi_sign_group_length"] == 10 / 4


def test_breakdown_and_period():
    docs = {"AA 1": {"site": "AA", "support": "tablet", "register": "administrative"}}
    assert baseline.breakdown([W], docs, "site") == {"AA": {"documents": 1, "sign_groups": 5, "identified_tokens": 10}}
    assert baseline.by_period([W, {**W, "period": None, "doc_key": "AA 2"}]) == {"(none given)": 1, "LM IB": 1}


def test_committed_report_matches_committed_json():
    """The report is generated from the JSON; neither may be edited by hand."""
    if not baseline.OUT_JSON.exists():
        return
    b = json.loads(baseline.OUT_JSON.read_text(encoding="utf-8"))
    assert baseline.render(b) == baseline.OUT_MD.read_text(encoding="utf-8")
    assert b["split"] == "train" and b["layer"] == "L0"
