from fractions import Fraction as F

from aegean.arithmetic import explore


def test_value_with_ligatures_and_unvalued():
    assert explore.value(5, ["JE"], explore.CORAZZA) == F(23, 4)
    assert explore.value(None, ["D", "D"], explore.CORAZZA) == F(1, 3)
    assert explore.value(2, ["W"], explore.CORAZZA) is None


def test_schrijver_matches_corazza_table3_combination_rows():
    s = explore.SCHRIJVER
    assert s["J"] + s["E"] + s["B"] == F(11, 12)  # "J E B" row, Schrijver column
    assert s["F"] + s["K"] == F(3, 16)  # "F K" row


def test_status():
    assert explore.status(F(10), F(10), True) == "exact"
    assert explore.status(F(160), F(159), True) == "near_miss_one_stroke"
    assert explore.status(F(160), F(159), False) == "mismatch"
    assert explore.status(None, F(1), True) == "unvalued"
