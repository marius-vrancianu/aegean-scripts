"""CI guardrails, run on pull requests.

1. Pre-registered hypotheses are immutable: any file under hypotheses/ that
   exists on the base branch may not be modified, renamed or deleted
   (hypotheses/outcomes/ and hypotheses/README.md / TEMPLATE.md excepted).
2. research-notes.md is append-only: the diff against base may add lines but
   not remove or change existing ones.
3. No held-out material: block paths or file contents under data/, src/,
   experiments/, tests/ or notebooks/ that reference the Knossos sceptre
   texts (KN Zg 57 / 58). A crude tripwire, not a guarantee. Lift it for a
   document only in the PR that adds it after predictions are frozen.
4. Review gate (CLAUDE.md -> Merging): a PR that changes anything under
   hypotheses/ or findings/ must contain or link (in the PR body) a review
   file docs/reviews/*.md whose last "Verdict:" line is "Verdict: APPROVE".
   With several reviews, at least one must end in APPROVE.
5. PR description headers (only when PR_BODY is set, i.e. in CI):
   - a PR that touches a rule file starts with "**Needs Marius's merge**";
   - otherwise, a review-gated PR starts with "**Review-gated:".

Limits: CI checks that an approving review file exists, not who wrote it,
and it cannot stop a merge by itself. It catches mistakes, not a determined
agent; the "Marius merges rule files by hand" rule still rests on CLAUDE.md.

Usage: python tools/check_guardrails.py <base-ref>
       (PR_BODY env var: the pull request description, set by CI)
"""
import os
import re
import subprocess
import sys

MUTABLE = ("hypotheses/outcomes/", "hypotheses/README.md", "hypotheses/TEMPLATE.md")
# Files allowed to *mention* the held-out documents (policy text, not data).
HELDOUT_POLICY_FILES = {
    "CLAUDE.md", "DATA_SOURCES.md", "research-notes.md", "README.md",
    "plans/phase2-analysis-plan.md", "docs/literature-survey-2026-10.md",
    "tools/check_guardrails.py", ".github/pull_request_template.md",
    "data/heldout.txt", "src/aegean/corpus/heldout.py", "tests/test_heldout.py",
    "tests/test_guardrails.py",  # tests the held-out regex, so it must name the documents
}
DATA_PATHS = ("data/", "src/", "experiments/", "tests/", "notebooks/")
HELDOUT_RE = re.compile(r"KN\s*Zg\s*0?5[78]", re.IGNORECASE)

GATED_PREFIXES = ("hypotheses/", "findings/")
RULE_FILES = ("CLAUDE.md", "tools/check_guardrails.py", "data/heldout.txt")
RULE_PREFIXES = (".github/",)
REVIEW_DIR = "docs/reviews/"
REVIEW_LINK_RE = re.compile(r"docs/reviews/[\w.\-]+\.md")
VERDICT_RE = re.compile(r"^\s*\**\s*Verdict:\s*\**\s*(APPROVE|CHANGES REQUESTED)\b", re.MULTILINE)


def is_rule_file(path: str) -> bool:
    return path in RULE_FILES or path.startswith(RULE_PREFIXES)


def last_verdict(text: str) -> str | None:
    """The last verdict line in a review file (re-reviews are appended)."""
    found = VERDICT_RE.findall(text)
    return found[-1] if found else None


def review_gate(touched: list[str], reviews: dict[str, str]) -> list[str]:
    """touched: paths changed by the PR; reviews: {path: text} of reviews in or linked from it."""
    gated = sorted(p for p in touched if p.startswith(GATED_PREFIXES))
    if not gated:
        return []
    if not reviews:
        return [f"review-gated paths changed ({', '.join(gated)}) but no review in {REVIEW_DIR} "
                "is added, changed or linked in the PR body"]
    verdicts = {p: last_verdict(t) for p, t in reviews.items()}
    if "APPROVE" in verdicts.values():
        return []
    shown = ", ".join(f"{p}: {v or 'no verdict line'}" for p, v in sorted(verdicts.items()))
    return [f"review-gated paths changed but no review ends in 'Verdict: APPROVE' ({shown})"]


def header_errors(touched: list[str], body: str) -> list[str]:
    first = body.strip().splitlines()[0] if body.strip() else ""
    if any(is_rule_file(p) for p in touched):
        if not first.startswith("**Needs Marius's merge**"):
            return ["rule files changed: PR description must start with \"**Needs Marius's merge**\""]
        return []
    if any(p.startswith(GATED_PREFIXES) for p in touched) and not first.startswith("**Review-gated:"):
        return ["review-gated PR: description must start with \"**Review-gated: <review file>**\""]
    return []


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def main(base: str) -> int:
    errors = []
    changes = git("diff", "--name-status", "-M", f"{base}...HEAD").splitlines()
    for line in changes:
        status, *paths = line.split("\t")
        old = paths[0]
        if old.startswith("hypotheses/") and not old.startswith(MUTABLE):
            if status[0] in "MDR":
                errors.append(f"pre-registered hypothesis changed ({status}): {old}")

    notes_diff = git("diff", "-U0", f"{base}...HEAD", "--", "research-notes.md")
    removed = [l for l in notes_diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    if removed:
        errors.append(f"research-notes.md is append-only; {len(removed)} line(s) removed or edited")

    added_files = [l.split("\t")[-1] for l in changes if l[0] in "AMR"]
    for path in added_files:
        # Prose (plans, hypotheses, findings) may name the documents;
        # only data, code and experiment outputs may not reference them.
        if path in HELDOUT_POLICY_FILES or not path.startswith(DATA_PATHS):
            continue
        if HELDOUT_RE.search(path):
            errors.append(f"held-out document in path: {path}")
            continue
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except (FileNotFoundError, IsADirectoryError):
            continue
        if HELDOUT_RE.search(text):
            errors.append(f"held-out document referenced in {path} (KN Zg 57/58); see CLAUDE.md")

    touched = sorted({p for l in changes for p in l.split("\t")[1:]})
    body = os.environ.get("PR_BODY")
    review_paths = {p for p in added_files if p.startswith(REVIEW_DIR) and p.endswith(".md")}
    if body:
        review_paths |= set(REVIEW_LINK_RE.findall(body))
    reviews = {}
    for p in sorted(review_paths):
        try:
            reviews[p] = open(p, encoding="utf-8").read()
        except FileNotFoundError:
            errors.append(f"linked review not found in the PR's tree: {p}")
    errors += review_gate(touched, reviews)
    if body is not None:
        errors += header_errors(touched, body)

    for e in errors:
        print(f"GUARDRAIL: {e}", file=sys.stderr)
    if not errors:
        print("guardrails OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "origin/main"))
