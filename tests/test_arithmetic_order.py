from aegean.arithmetic import order


def test_consistency_counts_majority_and_zero_for_ties():
    pairs = [("J", "E")] * 3 + [("E", "J")] + [("K", "L2"), ("L2", "K")]
    c, table = order.consistency(pairs)
    assert table["E|J"] == {"E>J": 1, "J>E": 3}
    assert c == 3 / 6  # J/E contributes 3, the K/L2 tie contributes 0


def test_identical_pairs_excluded():
    pairs, same = order.adjacent_pairs([["D", "D", "J"]])
    assert pairs == [("D", "J")] and same == 1


def test_cycle_detection():
    assert order.majority_cycles([("A", "B"), ("B", "C"), ("C", "A")]) == [["A", "B", "C"]]
    assert order.majority_cycles([("J", "E"), ("E", "F"), ("J", "F")]) == []


def test_permutation_null_is_deterministic():
    lists = [["J", "E"], ["E", "F"], ["J", "F", "K"]] * 3
    c, _ = order.consistency(order.adjacent_pairs(lists)[0])
    assert order.permutation_null(lists, c, 200) == order.permutation_null(lists, c, 200)


def test_decision_rule_matches_frozen_file():
    assert order.decide(14, 1.0, True, 0.0) == "inconclusive (insufficient data)"
    assert order.decide(30, 0.95, True, 0.001) == "supported"
    assert order.decide(30, 0.95, False, 0.001) == "inconclusive"
    assert order.decide(30, 0.70, True, 0.001) == "not supported"
    assert order.decide(30, 0.95, True, 0.06) == "not supported"
