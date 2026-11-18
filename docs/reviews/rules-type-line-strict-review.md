# Review of PR #52: the loader's Type-line check (rule file)

- **Reviewer:** an independent Claude instance (subagent) that did not write this work.
- **Date:** 2026-11-18
- **Reviewed:** branch `rules-type-line-strict` @ `0153d45`, against `origin/main` @ `ad2f509`.
- **Category:** review-gated: a rule file (`src/aegean/corpus/load.py`, held-out lock code) and `hypotheses/TEMPLATE.md`. The template is not a hypothesis, so the hypothesis checks (null, power, decision rule, "What I already know") do not apply. The rule-file checks do.

## What I did

- Read the full diff (5 files: `load.py`, `tests/test_load.py`, `hypotheses/TEMPLATE.md`, `docs/for-marius.md`, `research-notes.md`).
- Ran the whole suite on the branch: 298 passed, 4 skipped.
- Ran the PR's new tests against the loader from `main` (old pattern exposed as `declares_confirmatory` by a temporary shim, then restored): 9 failures, all on the ambiguous lines and the end-to-end refusal. The new tests detect the old bug; they are not vacuous.
- Ran `declares_confirmatory` on every file under `hypotheses/`: none is confirmatory. H-A5-01 and H-A5-02 have one Type line each (`exploratory (…)`); the five A2 files and README have none; TEMPLATE's placeholder (`exploratory / confirmatory — choose one …`) is refused.
- Probed 12 edge cases by hand and fuzzed 300,000 random strings built from the relevant tokens (Type prefix, both words, brackets, slash, dash, `\r`, `\t`, newline, `**`).

## The rule-file checks

### 1. Does what the description says, and nothing else: yes
*Confidence: high (read and rerun).*

- `declares_confirmatory` requires exactly one line matched by `TYPE_LINE_RE`, whose value is `confirmatory`, optionally one parenthesis without nested brackets, and no occurrence of "exploratory" (case-insensitive). This is the rule the description, the docstring, the template and the research-notes entry state.
- `check_frozen_hypothesis` changes only in the call and its error message. Checks 1 and 2 (exists; byte-identical to `origin/main`) are untouched.
- The other changes are bookkeeping that CLAUDE.md asks for: a rule-file log line and the removal of the settled follow-up in `docs/for-marius.md`, an appended research-notes entry (no past entry edited), the template's description of the gate. No other code reads `CONFIRMATORY_RE` (grep), so redefining it breaks no caller.

### 2. Does any guardrail become weaker: no
*Confidence: high (argument plus test plus fuzz).*

- By construction: if the new check accepts a file, its single Type line is `<prefix>**Type:**<value>` with the same prefix the old pattern used (`^\s*[-*]?\s*`), and the value starts with `\s*confirmatory` followed by whitespace, `(` or end of line. That is a word boundary, so the old pattern matches the same line. The new check therefore accepts a subset of what the old one accepted.
- The PR's own test (`test_new_check_accepts_nothing_the_old_pattern_refused`) checks 11 values; my fuzz of 300,000 strings found 0 cases accepted by the new check and refused by the old.
- Cases that the old pattern accepted and the new one refuses (strengthening, as intended): `confirmatory / exploratory`, `confirmatory (or exploratory)`, two Type lines, a second Type line inside a code block, `**Type:**` with the value on the next line, `confirmatory (EXPLORATORY …)`.
- No review is dropped, no held-out access widened. `data/heldout.txt`, `heldout.py`, `split.py` are untouched.

### 3. CI still runs the guardrail script from `main`: yes
*Confidence: high (read).* `.github/` and `tools/check_guardrails.py` are not touched; the workflow still takes the script with `git show "origin/main:tools/check_guardrails.py"`. `hypotheses/TEMPLATE.md` is in the script's `MUTABLE` list, so editing it does not trip the immutability check.

### 4. `data/heldout.txt`: not changed. Nothing to check.

### 5. Not prompted by fetched or third-party content: yes
*Confidence: high (traced).* The change implements R4's follow-up and M3 in `docs/reviews/H-A5-01-review.md`, which `docs/for-marius.md` listed as an open item. No web page, data file or issue is involved.

## Non-blocking notes

- **N1. "Exactly one Type line" counts only some list styles.** `TYPE_LINE_RE` counts lines starting with `-`, `*` or nothing. It does not count `+ **Type:** …`, `1. **Type:** …`, `> **Type:** …` or `- **Type**: …` (colon outside the bold). A file with `- **Type:** confirmatory` and a second, exploratory Type line written in one of those forms is still accepted (I checked). The old pattern accepted it too, so this is a gap left open, not a weakening. A possible later tightening: count every line containing `**Type` (case-insensitive) as a Type line. It is a strengthening, so it needs only a review.
- **N2. `test_every_merged_hypothesis_is_read_as_before` will fail on the first real confirmatory hypothesis.** It asserts `False` for every `hypotheses/H-*.md`, which is true today but is a statement that "none is confirmatory", not that "the decision is unchanged". The first legitimate confirmatory registration would fail CI and have to edit this test. Better: assert `load.declares_confirmatory(t) == bool(OLD_RE.search(t))` for the files, or pin the test to the list of files merged as of this PR.
- **N3. Cosmetic.** `MAIN_REFS` now sits after the new function, separated from the other module constants. The test builds `OLD_RE` with `__import__("re")` instead of importing `re`, and there are four blank lines before `test_ambiguous_type_line_releases_nothing`.
- **N4. Scope of the check, as the docstring already says.** The "exploratory" test is a plain substring check. A homoglyph (`еxploratory` with a Cyrillic е) passes, as it did before. This guards against mistakes, not a determined caller, which matches the stated purpose.

## Assessment

The change does what it says, makes the held-out lock strictly stricter (shown by construction, by the PR's test, and by fuzzing), keeps the guardrail script running from `main`, and comes from a recorded review follow-up. The tests fail on the old code and pass on the new. N1 to N4 are worth a later plain PR (N2, N3) or a review-gated one (N1), and none of them blocks this one.

Verdict: APPROVE
