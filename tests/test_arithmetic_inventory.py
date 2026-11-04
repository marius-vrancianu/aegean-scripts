from aegean.arithmetic.inventory import classify

BASE = dict(total_integer=95, total_fractions="", total_damaged=False, scope_entries=3,
            scope_damaged=0, scope_unlabelled=0, doc_warnings=0, n_markers_in_doc=1)


def test_classify_rules_in_order():
    assert classify({**BASE})[0] == "complete"
    assert classify({**BASE, "total_integer": "", "total_fractions": ""})[1].startswith("R1")
    assert classify({**BASE, "scope_entries": 0})[1].startswith("R2")
    assert classify({**BASE, "total_damaged": True})[1].startswith("R3")
    assert classify({**BASE, "scope_damaged": 1})[1].startswith("R4")
    assert classify({**BASE, "n_markers_in_doc": 2})[1].startswith("R5")
