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
