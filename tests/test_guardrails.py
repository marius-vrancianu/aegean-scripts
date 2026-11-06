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


def test_header_rules():
    assert cg.header_errors(["CLAUDE.md", "findings/x.md"], "**Review-gated: docs/reviews/x.md**")
    assert cg.header_errors(["CLAUDE.md"], "**Needs Marius's merge**: rules") == []
    assert cg.header_errors(["findings/x.md"], "**Merge:** auto-merge")
    assert cg.header_errors(["findings/x.md"], "**Review-gated: docs/reviews/x.md**") == []
    assert cg.header_errors(["src/a.py"], "") == []
