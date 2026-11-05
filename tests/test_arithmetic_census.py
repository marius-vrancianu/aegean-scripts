from aegean.arithmetic import census
from aegean.arithmetic.census import Row

OK = {"total_intact": "yes", "scope_entries_intact": "yes", "entry_area_complete": "yes"}


def row(total, entries, scope="S1", tfr=()):
    return Row("X1", "KU-RO", 5, scope, total, list(tfr), [(e, [], False) for e in entries])


def test_tablet_of():
    assert census.tablet_of("HT122a") == "HT122" and census.tablet_of("HT13") == "HT13"
    assert census.tablet_of("HT123+124b") == "HT123+124"


def test_category_order():
    assert census.categorize(row(None, [1]), OK).category.startswith("1")
    assert census.categorize(row(5, [1], tfr=["J"]), OK).category.startswith("2")
    assert census.categorize(row(5, [5]), {**OK, "total_intact": "partly"}).category.startswith("3")
    assert census.categorize(row(5, []), OK).category.startswith("4")
    assert census.categorize(row(6, [3, 3]), OK).category.startswith("5")
    assert census.categorize(row(16, [3, 3]), OK).category.startswith("6")
    assert census.categorize(row(30, [3, 3]), {**OK, "entry_area_complete": "no"}).category.startswith("7")
    assert census.categorize(row(30, [3, 3]), OK).category.startswith("8")
    assert census.categorize(row(2, [3, 3]), {**OK, "entry_area_complete": "no"}).category.startswith("8")


def test_permutation_test_and_decision():
    pairs = [(10, 10), (20, 20), (31, 31), (45, 45), (7, 70)]
    t = census.permutation_test(pairs, 2000)
    assert t["observed_consistent"] == 4 and t["p"] < 0.05
    assert census.decide({"n": 4, "p": 0.0}).startswith("descriptive")


def test_s1_starts_after_a_marker_without_number():
    KI, RO, KU = "AB067", "AB002", "AB081"
    g = lambda *s: {"type": "group", "signs": list(s), "value": None, "fractions": [], "damaged_left": False, "damaged_right": False, "flags": [], "raw": ""}
    n = lambda v: {"type": "numeral", "signs": [], "value": v, "fractions": [], "damaged_left": False, "damaged_right": False, "flags": [], "raw": ""}
    doc = {"id": "T1", "lines": [[g("AB001"), n(20)], [g(KI, RO)], [g("AB002"), n(1)], [g("AB003"), n(1)], [g(KU, RO), n(2)]]}
    s1 = [r for r in census.build_rows([doc]) if r.scope == "S1"][0]
    assert [e[0] for e in s1.entries] == [1, 1]
