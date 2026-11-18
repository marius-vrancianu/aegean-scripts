"""The Tier 1 batch (A5.17; hypotheses/H-A5-01.md, Part 1): registration check and Benjamini–Hochberg."""
import json
import subprocess

import pytest

from aegean.benchmark import batch

PAIR_FILE = "# H-A5-{n} — pair\n\n- **Type:** exploratory\n- **Protocol:** H-A5-01\n"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                    "-c", "commit.gpgsign=false", *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    h = tmp_path / "hypotheses"
    h.mkdir()
    (h / "H-A5-01.md").write_text("# H-A5-01 — protocol\n", encoding="utf-8")
    (h / "H-A5-02.md").write_text(PAIR_FILE.format(n="02"), encoding="utf-8")
    (h / "H-A5-07.md").write_text("# H-A5-07 — no protocol line\n", encoding="utf-8")
    (h / "H-A5-04.md").write_text(PAIR_FILE.format(n="04").replace("H-A5-01\n", "H-A5-09\n"), encoding="utf-8")
    (h / "H-A5-08.md").write_text(PAIR_FILE.format(n="08"), encoding="utf-8")  # a new pair naming the closed H-A5-01
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def test_registered_files_pass_and_name_their_protocol(repo):
    assert batch.check_registered("H-A5-01", repo) == "H-A5-01"
    assert batch.check_registered("H-A5-02", repo) == "H-A5-01"


def test_a_pair_under_the_second_protocol(repo):
    (repo / "hypotheses/H-A5-03.md").write_text("# H-A5-03 — protocol v2\n", encoding="utf-8")
    (repo / "hypotheses/H-A5-05.md").write_text(PAIR_FILE.format(n="05").replace("H-A5-01\n", "H-A5-03\n"), encoding="utf-8")
    (repo / "hypotheses/H-A5-06.md").write_text(PAIR_FILE.format(n="06") + "- **Protocol:** H-A5-03\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "v2")
    assert batch.check_registered("H-A5-03", repo) == "H-A5-03"
    assert batch.check_registered("H-A5-05", repo) == "H-A5-03"
    with pytest.raises(batch.NotRegistered, match="must name its protocol"):  # two Protocol lines
        batch.check_registered("H-A5-06", repo)


def test_batches_are_kept_apart(tmp_path):
    """The same pair may be run under both protocols; each batch sees only its own runs."""
    def result(h, bp, p1):
        return {"protocol": h, "batch_protocol": bp, "method": "M1", "rules": None,
                "lexicon": {"name": "x", "forms": 1, "sha256": "s"}, "test1": {"p": p1}, "test2": {"p": 0.5}}
    (tmp_path / "M1-x.json").write_text(json.dumps(result("H-A5-01", "H-A5-01", 0.3)), encoding="utf-8")
    old = result("H-A5-01", "H-A5-01", 0.3)
    del old["batch_protocol"]  # files written before the field existed belong to H-A5-01
    (tmp_path / "old.json").write_text(json.dumps({**old, "protocol": "H-A5-02", "lexicon": {"name": "y"}}), encoding="utf-8")
    new = result("H-A5-04", "H-A5-03", 0.2)
    assert [r["hypothesis"] for r in batch.records(tmp_path, "H-A5-01")] == ["H-A5-01", "H-A5-02"]
    assert batch.records(tmp_path, "H-A5-03") == []
    table, _ = batch.update(tmp_path, new, "H-A5-04-M1-x", "H-A5-03")  # same pair as M1-x, other protocol: allowed
    assert [r["hypothesis"] for r in table] == ["H-A5-04"]
    batch.write(tmp_path, table, [], "H-A5-03")
    assert (tmp_path / "batch-H-A5-03.md").exists() and not (tmp_path / "batch.md").exists()
    assert "hypotheses/H-A5-03.md" in (tmp_path / "batch-H-A5-03.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("hid, why", [
    ("H-A5-99", "does not exist"),
    ("H-A2-04", "not an A5 hypothesis"),
    ("../H-A5-01", "not an A5 hypothesis"),
    ("H-A5-07", "must name its protocol"),
    ("H-A5-04", "must name its protocol"),
    ("H-A5-08", "closed to new pairs"),
])
def test_unregistered_files_are_refused(repo, hid, why):
    with pytest.raises(batch.NotRegistered, match=why):
        batch.check_registered(hid, repo)


def test_unmerged_and_changed_files_are_refused(repo):
    (repo / "hypotheses/H-A5-05.md").write_text(PAIR_FILE.format(n="05"), encoding="utf-8")
    with pytest.raises(batch.NotRegistered, match="not on main"):
        batch.check_registered("H-A5-05", repo)
    with (repo / "hypotheses/H-A5-02.md").open("a", encoding="utf-8") as f:
        f.write("an edit after the merge\n")
    with pytest.raises(batch.NotRegistered, match="differs from the merged version"):
        batch.check_registered("H-A5-02", repo)


def test_a_branch_is_not_main(repo):
    git(repo, "checkout", "-q", "-b", "feature")
    (repo / "hypotheses/H-A5-05.md").write_text(PAIR_FILE.format(n="05"), encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "on a branch")
    with pytest.raises(batch.NotRegistered, match="not on main"):
        batch.check_registered("H-A5-05", repo)


def test_no_main_ref(tmp_path):
    (tmp_path / "hypotheses").mkdir()
    (tmp_path / "hypotheses/H-A5-01.md").write_text("x", encoding="utf-8")
    git(tmp_path, "init", "-q", "-b", "trunk")
    with pytest.raises(batch.NotRegistered, match="no origin/main or main ref"):
        batch.check_registered("H-A5-01", tmp_path)


def rec(h, p1, p2, key=None, stem=None):
    return {"stem": stem or f"{h}-M1-x", "hypothesis": h, "method": "M1", "lexicon": "x", "pair_key": key or h,
            "p1": p1, "p2": p2, "p_pair": max(p1, p2)}


def test_label_and_correction():
    """The correction can only turn a would-be C into B, never touch an A or the first two kinds of B."""
    table = batch.apply([rec("H-A5-01", 0.40, 0.84), rec("H-A5-02", 0.01, 0.03), rec("H-A5-03", 0.02, 0.90),
                         rec("H-A5-04", 0.90, 0.001), rec("H-A5-05", 0.002, 0.004)])
    out = {r["hypothesis"]: r for r in table}
    assert out["H-A5-01"]["outcome"] == batch.LABEL_A
    assert out["H-A5-03"]["outcome"] == batch.LABEL_B1
    assert out["H-A5-04"]["outcome"] == batch.LABEL_B2
    assert out["H-A5-05"]["p_adjusted"] == pytest.approx(0.004 * 5 / 1) and out["H-A5-05"]["outcome"] == batch.LABEL_C
    assert out["H-A5-02"]["p_adjusted"] == pytest.approx(0.03 * 5 / 2) and out["H-A5-02"]["outcome"] == batch.LABEL_B3
    assert batch.label(0.04, 0.04, 0.04) == batch.LABEL_C and batch.label(0.04, 0.04, 0.051) == batch.LABEL_B3
    assert batch.label(0.05, 0.051, 0.0) == batch.LABEL_B1  # the boundary is inclusive, as registered


def test_adding_pairs_can_turn_an_earlier_c_into_b_and_the_change_is_reported():
    before = batch.apply([rec("H-A5-01", 0.40, 0.84), rec("H-A5-02", 0.01, 0.02)])
    assert before[1]["p_adjusted"] == pytest.approx(0.04) and before[1]["outcome"] == batch.LABEL_C  # 0.02 * 2 / 1
    after = batch.apply(batch.admit(before, rec("H-A5-03", 0.70, 0.60)))
    assert after[1]["p_adjusted"] == pytest.approx(0.06) and after[1]["outcome"] == batch.LABEL_B3  # 0.02 * 3 / 1
    assert after[0]["outcome"] == batch.LABEL_A
    assert batch.changes(before, after) == [f"H-A5-02 (H-A5-02-M1-x): {batch.LABEL_C} → {batch.LABEL_B3}"]


def test_admit_rules():
    recs = [rec("H-A5-01", 0.4, 0.8, key="k1", stem="M1-hebrew-strong-verbs")]
    assert [r["p1"] for r in batch.admit(recs, rec("H-A5-01", 0.4, 0.8, key="k1", stem="M1-hebrew-strong-verbs"))] == [0.4]
    with pytest.raises(batch.BatchError, match="one hypothesis is one pair"):
        batch.admit(recs, rec("H-A5-01", 0.4, 0.8, key="k2"))
    with pytest.raises(batch.BatchError, match="already run under H-A5-01"):
        batch.admit(recs, rec("H-A5-02", 0.4, 0.8, key="k1"))
    with pytest.raises(batch.BatchError, match="belongs to H-A5-01"):
        batch.admit(recs, rec("H-A5-02", 0.4, 0.8, key="k2", stem="M1-hebrew-strong-verbs"))
    assert batch.stem_for(recs, "H-A5-01", "M1", "x") == "M1-hebrew-strong-verbs"
    assert batch.stem_for(recs, "H-A5-02", "M1", "semitic-pool") == "H-A5-02-M1-semitic-pool"


def test_batch_is_capped():
    with pytest.raises(batch.BatchError, match="at most 50"):
        batch.apply([rec(f"H-A5-{i:02d}", 0.5, 0.5) for i in range(1, 52)])


def test_the_committed_batch_reproduces_from_the_results_files(tmp_path):
    """batch.md and batch.json in the repo are what `python -m aegean.benchmark.batch` makes from the results."""
    import shutil
    from aegean.benchmark import tier1
    out = tmp_path / "results"
    shutil.copytree(tier1.OUT_DIR, out)
    committed = {n: (tier1.OUT_DIR / n).read_text(encoding="utf-8") for n in ("batch.json", "batch.md")}
    (out / "batch.json").unlink()
    assert batch.main(["--out", str(out)]) == 0
    assert {n: (out / n).read_text(encoding="utf-8") for n in committed} == committed
    pairs = json.loads(committed["batch.json"])["pairs"]
    assert pairs[0]["hypothesis"] == "H-A5-01" and pairs[0]["outcome"] == batch.LABEL_A
    assert pairs[0]["p_pair"] == pytest.approx(0.8401598401598401)
