import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "check_guardrails", Path(__file__).resolve().parents[1] / "tools" / "check_guardrails.py"
)
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)


def test_heldout_regex_matches_common_spellings():
    for s in ("KN Zg 57", "KNZg57a", "kn zg 58", "KN Zg 057"):
        assert cg.HELDOUT_RE.search(s), s


def test_heldout_regex_ignores_other_documents():
    for s in ("KN Zg 55", "KNZg5", "HT 57"):
        assert not cg.HELDOUT_RE.search(s), s


APPROVE = "# Review\n\nfindings fine\n\nVerdict: APPROVE\n"
CHANGES = "# Review\n\nVerdict: CHANGES REQUESTED\n"


def test_review_gate_not_triggered_by_code():
    assert cg.review_gate(["src/aegean/x.py", "tests/t.py"], {}) == []


def test_review_gate_requires_a_review():
    assert cg.review_gate(["findings/003-x.md"], {})


def test_review_gate_uses_last_verdict():
    rereview = CHANGES + "\n## Re-review\n\nVerdict: APPROVE\n"
    assert cg.review_gate(["hypotheses/H-A1-01.md"], {"docs/reviews/h.md": rereview}) == []
    flipped = APPROVE + "\n## Re-review\n\nVerdict: CHANGES REQUESTED\n"
    assert cg.review_gate(["hypotheses/H-A1-01.md"], {"docs/reviews/h.md": flipped})


def test_review_gate_bold_verdict_and_no_verdict():
    assert cg.last_verdict("**Verdict: APPROVE**") == "APPROVE"
    assert cg.review_gate(["findings/x.md"], {"docs/reviews/x.md": "no verdict here"})


def test_rule_files_are_review_gated():
    for path in ("CLAUDE.md", "tools/check_guardrails.py", ".github/workflows/ci.yml", "data/heldout.txt"):
        assert cg.is_gated(path), path
        assert cg.review_gate([path], {})
        assert cg.review_gate([path], {"docs/reviews/r.md": APPROVE}) == []
        assert cg.review_gate([path], {"docs/reviews/r.md": CHANGES})
    for path in ("src/aegean/corpus/load.py", "src/aegean/corpus/heldout.py", "src/aegean/corpus/split.py"):
        assert cg.is_gated(path), path  # the code that enforces the held-out lock
    assert not cg.is_gated("docs/heldout-split.md") and not cg.is_gated("src/aegean/corpus/baseline.py")


def test_only_reviews_the_pr_adds_or_changes_count():
    # An approval that sits in the tree from another PR is not in the PR's changed files.
    assert cg.counted_reviews(["CLAUDE.md", "src/a.py"]) == set()
    assert cg.counted_reviews(["CLAUDE.md", "docs/reviews/rules-x-review.md", "docs/reviews/notes.txt"]) == {
        "docs/reviews/rules-x-review.md"}
    assert cg.review_gate(["CLAUDE.md"], {p: APPROVE for p in cg.counted_reviews(["CLAUDE.md"])})


def test_linked_but_unchanged_review_does_not_open_the_gate(tmp_path, monkeypatch):
    """End to end on a throwaway repository: PR changes CLAUDE.md and links an old approval."""
    import subprocess

    def git(*a):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false",
                        *a], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "docs/reviews").mkdir(parents=True)
    (tmp_path / "docs/reviews/old-review.md").write_text(APPROVE, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("rules\n", encoding="utf-8")
    (tmp_path / "research-notes.md").write_text("notes\n", encoding="utf-8")
    git("init", "-q", "-b", "main"); git("add", "."); git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "pr")
    (tmp_path / "CLAUDE.md").write_text("weaker rules\n", encoding="utf-8")
    git("commit", "-q", "-am", "change rules")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PR_BODY", "**Review-gated: docs/reviews/old-review.md**")
    assert cg.main("main") == 1
    (tmp_path / "docs/reviews/new-review.md").write_text(APPROVE, encoding="utf-8")
    git("add", "."); git("commit", "-q", "-m", "review")
    monkeypatch.setenv("PR_BODY", "**Review-gated: docs/reviews/new-review.md**")
    assert cg.main("main") == 0


def test_header_rules():
    ok = "**Review-gated: docs/reviews/x.md**"
    assert cg.header_errors(["CLAUDE.md", "findings/x.md"], ok) == []
    assert cg.header_errors(["CLAUDE.md"], ok) == []
    assert cg.header_errors(["CLAUDE.md"], "**Needs Marius's merge**: rules")  # the old header no longer passes
    assert cg.header_errors(["data/heldout.txt"], "**Merge:** merges when CI is green")
    assert cg.header_errors(["findings/x.md"], "**Merge:** auto-merge")
    assert cg.header_errors(["findings/x.md"], ok) == []
    assert cg.header_errors(["src/a.py"], "") == []


OLD = "# comment\nlineara.xyz:X1\nsplit:HT 1\nsplit:HT 2\n"


def test_heldout_additions_and_comment_edits_need_no_tag():
    new = "# another comment\nlineara.xyz:X1\nsplit:HT 1\nsplit:HT 2\nsplit:HT 3\n"
    assert cg.heldout_removal_errors(OLD, new, "", lambda t: False) == []


def test_heldout_removal_needs_an_existing_frozen_prediction_tag():
    new = "# comment\nlineara.xyz:X1\nsplit:HT 1\n"
    assert cg.heldout_removal_errors(OLD, new, "no tag here", lambda t: True)
    assert cg.heldout_removal_errors(OLD, new, None, lambda t: True)
    body = "**Review-gated: docs/reviews/x.md**\n\nFrozen-prediction tag: predictions-a3-v1\n"
    assert cg.heldout_removal_errors(OLD, new, body, lambda t: t == "predictions-a3-v1") == []
    assert cg.heldout_removal_errors(OLD, new, body, lambda t: False)
    assert cg.heldout_removal_errors(OLD, new, "**Frozen-prediction tag:** `predictions-v1`", lambda t: True) == []


def test_a_release_tag_is_not_a_frozen_prediction_tag():
    new = "# comment\nlineara.xyz:X1\nsplit:HT 1\n"
    for name in ("corpus-v1.0", "v1", "corpus-predictions-1"):
        assert cg.heldout_removal_errors(OLD, new, f"Frozen-prediction tag: {name}", lambda t: True), name


def test_ci_runs_the_guardrail_script_from_main():
    ci = (Path(__file__).resolve().parents[1] / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert 'git show "origin/main:tools/check_guardrails.py"' in ci
    assert "python tools/check_guardrails.py" not in ci
