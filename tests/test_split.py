"""The held-out split (A1.12). Synthetic populations, plus the reproducibility check on the frozen list."""
from fractions import Fraction

from aegean.corpus import split
from aegean.corpus.heldout import load_heldout, load_split


def _rows(sizes):
    return [{"key": f"{site} {support} {i}", "site": site, "support": support, "analysis_default": "true"}
            for (site, support), n in sizes.items() for i in range(n)]


SIZES = {("AA", "tablet"): 139, ("AA", "nodule"): 26, ("BB", "tablet"): 85, ("BB", "roundel"): 22,
         ("CC", "tablet"): 5, ("CC", "vessel"): 4, ("DD", "tablet"): 1, ("EE", "vessel"): 8}


def test_small_strata_stay_in_training():
    q = split.quotas(SIZES)
    assert q[("CC", "vessel")] == 0 and q[("DD", "tablet")] == 0
    assert q[("CC", "tablet")] == 1  # five documents is the smallest stratum that is split


def test_quotas_total_is_the_rounded_fraction_of_eligible_documents():
    q = split.quotas(SIZES)
    eligible = sum(n for n in SIZES.values() if n >= 5)
    assert sum(q.values()) == round(eligible / 5) == 57
    for s, n in SIZES.items():
        if n >= 5:
            assert abs(q[s] - Fraction(n, 5)) < 1  # floor or ceiling of the exact share


def test_quota_remainders_go_to_largest_fractional_parts_then_name_order():
    # Exact shares 1.2, 1.2, 1.6: target round(4.0) = 4, floors sum to 3, the 0.6 remainder wins.
    q = split.quotas({("A", "x"): 6, ("B", "x"): 6, ("C", "x"): 8})
    assert q == {("A", "x"): 1, ("B", "x"): 1, ("C", "x"): 2}
    # Tie on remainders (three times 1.4, target 4): the first stratum in name order gets the extra one.
    q = split.quotas({("B", "x"): 7, ("A", "x"): 7, ("C", "x"): 7})
    assert q == {("A", "x"): 2, ("B", "x"): 1, ("C", "x"): 1}


def test_draw_is_deterministic_stratified_and_order_independent():
    rows = _rows(SIZES)
    held, table = split.draw(rows, seed=1)
    assert (held, table) == split.draw(list(reversed(rows)), seed=1)
    assert len(held) == 57 == len(set(held))
    assert sum(k.startswith("AA tablet ") for k in held) == table[("AA", "tablet")]["heldout"] == 28
    assert not any(k.startswith(("CC vessel", "DD tablet")) for k in held)
    assert table[("CC", "vessel")] == {"documents": 4, "heldout": 0, "training": 4, "split": False}


def test_draw_depends_on_the_seed():
    rows = _rows(SIZES)
    assert split.draw(rows, seed=1)[0] != split.draw(rows, seed=2)[0]


def test_rank_is_a_plain_sha256_anyone_can_recompute():
    import hashlib
    assert split.rank(7, "HT 13") == hashlib.sha256(b"7|HT 13").hexdigest()


def test_render_replaces_only_the_generated_block():
    text = "# header\nlineara.xyz:X1\n"
    once = split.render(text, ["A 1", "B 2"])
    assert once.startswith(text) and "split:A 1\nsplit:B 2\n" in once
    assert split.render(once, ["A 1", "B 2"]) == once
    assert "split:B 2" not in split.render(once, ["A 1"])


def test_split_lines_are_not_ingest_exclusions(tmp_path):
    p = tmp_path / "heldout.txt"
    p.write_text(split.render("lineara.xyz:X1\n", ["HT 13"]), encoding="utf-8")
    assert load_heldout(p) == {"lineara.xyz": {"X1"}}
    assert load_split(p) == {"HT 13"}


def test_frozen_split_reproduces_from_the_committed_seed_and_document_list():
    """data/heldout.txt must equal a fresh draw: nobody can add or remove a held-out document by hand."""
    frozen = load_split()
    if not frozen:  # before the freeze commit
        return
    held, table = split.draw(split.read_population())
    assert sorted(frozen) == held
    assert all(t["heldout"] == 0 for t in table.values() if t["documents"] < split.MIN_STRATUM)
