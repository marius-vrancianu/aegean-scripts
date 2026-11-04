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

Usage: python tools/check_guardrails.py <base-ref>
"""
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
}
DATA_PATHS = ("data/", "src/", "experiments/", "tests/", "notebooks/")
HELDOUT_RE = re.compile(r"KN\s*Zg\s*0?5[78]", re.IGNORECASE)


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

    for e in errors:
        print(f"GUARDRAIL: {e}", file=sys.stderr)
    if not errors:
        print("guardrails OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "origin/main"))
