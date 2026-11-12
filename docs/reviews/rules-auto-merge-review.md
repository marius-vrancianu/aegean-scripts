# Review: PR #38 — no manual merges; rule files review-gated; guardrails from the base branch

Reviewer: independent Claude instance (subagent, did not write the work). Date: 2026-11-12.
Reviewed commit: `6788a29` against `main` @ `27b2e99`.

## Read this first

- **Green CI on this PR is not an approval.** CI judges this PR with the script on `main`, which has no review gate for rule files. Its only complaint was that this file did not exist. It turns green as soon as this file is pushed, whatever the verdict below says.
- **The verdict is CHANGES REQUESTED.** Two checks that replace the human merge can be satisfied without doing what they are meant to prove (B1, B2). Both are small fixes.
- **I could not verify Marius's instruction or his waiver** (B3). I do not doubt the account; the only record is text written by the author session.

## What I checked

| Check | Result |
|---|---|
| Diff does what the description says | Yes, with three small undisclosed changes (N6) |
| `pytest -q` on the branch | 198 passed, 15 skipped |
| Base-branch script on this PR (as CI runs it) | One error: linked review file missing. Nothing else |
| CI failure on `6788a29` | Same single error (job log) |
| `data/heldout.txt` | Unchanged |
| `hypotheses/`, `findings/` | Untouched |
| `research-notes.md` | Append only |
| Rulesets as described | Yes: `main-protection` (required check `test`, merge commits only, no bypass actors); `corpus-tags` (no update or deletion of `corpus-*`) |
| CI takes the script from the base branch | Yes (`git show "origin/$BASE_REF:tools/check_guardrails.py"`), and a test pins it |
| Weakening stated, instruction cited | Stated plainly, in the third paragraph and in research-notes. Instruction quoted, not verifiable (B3) |
| Prompted by fetched or third-party text | No sign of it. The notes attribute the change to Marius in session |

## Blocking

### B1. The review gate accepts an old approval from another PR

`main()` collects review files that the PR adds or changes **or that the description links**, and `review_gate` passes if any of them ends in APPROVE. A linked file only has to exist in the tree.

Reproduced on this branch with the PR's own script:

```
PR_BODY='**Review-gated: docs/reviews/finding-002-review.md**' python tools/check_guardrails.py origin/main
guardrails OK
```

That is this PR's full diff (CLAUDE.md, the script, the workflow) passing on the approval of Finding 002.

- The hole exists on `main` today for hypotheses and findings. It was tolerable while a human merged rule files.
- After this PR the gate is the only thing between a rule change and `main`.
- It does not need a determined agent. A description that mentions an earlier review for context is enough.

**Requested:** count an APPROVE only from a review file that the PR itself adds or modifies. Linked files that are unchanged against the base do not count. Add a test. Re-reviews append to the same file, so they still qualify.

Confidence: high (reproduced).

### B2. The held-out lock accepts any tag, including `corpus-v1.0`

`heldout_removal_errors` checks that the named tag exists. It does not check what the tag is. `Frozen-prediction tag: corpus-v1.0` passes today.

- CLAUDE.md now says "Held-out data keeps its own lock, whoever merges" and "Blindness cannot be restored by a revert". The second sentence is the reason the first has to be true.
- No naming convention for frozen-prediction tags exists anywhere in the repository (searched: only the test uses `predictions-a3-v1`).

**Requested:**
1. Fix a prefix in CLAUDE.md (for example `predictions-*`) and have the check accept only tags with it.
2. Add an item to `docs/for-marius.md`: extend the tag ruleset to that prefix (no update, no deletion). Only he can change settings.

Confidence: high for the behaviour (read from the code and the tag list). The prefix is my suggestion, not a requirement of the plan.

### B3. Who merges this PR

- Under the rules in force on `main`, this is a hand-merge PR: "Never enable auto-merge and never merge it yourself."
- The description says Marius waived that in chat. The research-notes entry says the same. Both were written by the author session. I searched the earlier conversations I can reach and found the 2026-11-06 policy discussions, not the 2026-11-12 one.
- Agents act under Marius's account, so nothing on GitHub can tell his action from an agent's.

I am not asking for a change to the PR here. I am recording that this review does not confirm the waiver, and that it cannot. One click on "Merge" in the web interface by Marius, after B1 and B2 are fixed and re-reviewed, would settle it and fits how he says he works. If he has told the author session to merge, that is between him and that session.

## Not blocking, recommended

**N1. The loader gate is not a rule file.** `src/aegean/corpus/load.py`, `heldout.py` and `split.py` can change in a plain PR with no review. The test asserts that `heldout.py` is not gated. So "the split is read only through `aegean.corpus.load`" rests on unreviewed code, and the new `split.py` docstring promises "an independent review" that nothing requires. This is not made worse by the PR. Adding the three files to `RULE_FILES` is a strengthening and needs no instruction.

**N2. A `.github/` PR is not gated at all.** A `pull_request` run uses the PR's own workflow file. A PR that deletes the guardrail step passes with no review. The description names this gap. But the CLAUDE.md sentence "CI fails such a PR until an approving review is in it" is false for exactly this case; say so there. Possible follow-up (untested, medium confidence): a second workflow on `pull_request_target`, which GitHub takes from the base branch, running only the base script over the PR's files.

**N3. "Script from `main`" is really "script from the PR's base branch".** For a stacked PR the base is an agent-made branch. The final PR into `main` is still judged by `main`, so the gate holds. Fix the wording, or hardcode `origin/main`.

**N4. Fallback removed.** The old text covered a session that is blocked from merging ("say so in the PR, Marius merges"). Earlier sessions were blocked (403). The new text has no such case. Suggest: note it in the PR and list it in `docs/for-marius.md`.

**N5. Marius's revert lever needs him to see rule changes.** The instruction behind a weakening is asserted by the author and cannot be checked by a reviewer (see B3). Suggest a third list in `docs/for-marius.md`: rule-file PRs merged, one line each, marked if they weaken anything. This PR would be its first entry.

**N6. Undisclosed in the description.** None is harmful.
- The author may now tell the reviewer the repository and checkout path.
- The reviewer's report is "recorded in the PR or in `docs/for-marius.md`" instead of relayed to Marius.
- "If unsure" now defaults to review-gated instead of hand-merge (follows from the change, but is a default getting weaker).

## What gets weaker, in my words

The description is honest about it. A rule change used to need a human. It will need a second Claude instance and CI. With B1 open, it needs neither. With B1 and B2 fixed, the remaining risks are the ones the description lists: a blind spot shared by author and reviewer, and edits to the workflow file.

## To approve

1. B1 fixed with a test.
2. B2 fixed with a test, and the settings item added to `docs/for-marius.md`.
3. N2's one-sentence correction in CLAUDE.md (the rest of N1–N6 at the author's choice).

Verdict: CHANGES REQUESTED

---

## Re-review, 2026-11-12

Reviewer: a second independent Claude instance (subagent; wrote neither the work nor the first review).
Reviewed commit: `76f0964` against `main` @ `27b2e99`. This re-review covers that commit only. Anything pushed after it, other than this file, is unreviewed.

### Scope of the verdict

- **The verdict below is about the content of the PR. It is not an authorisation to merge it.** Under the rules on `main`, this PR is merged by Marius. Whether he waived that is between him and the author session (B3, still open).
- **I could not confirm the 2026-11-12 instruction either.** I searched the conversations I can reach. Confidence in each point: high for what I found, none for what I could not see.
  - 2026-11-06: Marius himself proposed "how about we deactivate all manual merges?". The outcome then kept rule files manual.
  - 2026-11-11 (latest conversation I can see): rule-file PRs still needed his merge.
  - 2026-11-12: nothing reachable. The direction fits what he asked for on 11-06; the instruction itself and the waiver rest on the author session's text.
- **Cheapest way to settle it:** Marius clicks **Merge pull request** on #38 in the web interface. It costs one click and makes the last hand-merge the one that ends hand-merges.

### What I checked

| Check | Result |
|---|---|
| `pytest -q` at `76f0964` | 201 passed, 15 skipped |
| **B1** fixed | Yes. The first review's reproduction (`PR_BODY` linking `finding-002-review.md`) now exits 1 with two errors. An end-to-end test covers it |
| **B2** fixed | Yes. `corpus-v1.0`, `v1`, `corpus-predictions-1` are rejected; prefix and existence are both tested. S1 is in `docs/for-marius.md` |
| **N2** sentence in CLAUDE.md | Present ("CI cannot be relied on there and the rule alone binds you") |
| N1, N3, N4, N5, N6 | All taken. `ci.yml` now reads `origin/main:tools/check_guardrails.py`; a test pins it |
| `main`'s script on this PR, as CI runs it | `guardrails OK`. CI on `76f0964`: success |
| The PR's own script on this PR | Fails as it should: review ends in CHANGES REQUESTED; old header |
| `data/heldout.txt`, `hypotheses/`, `findings/` | Untouched |
| `research-notes.md` | Append only (two new entries) |
| Rulesets | `main-protection`: required check `test`, merge commits only, no bypass actors. `corpus-tags`: `refs/tags/corpus-*`, no update or deletion. As described |
| Weakening stated, instruction cited | Stated plainly in the description, the notes and the `for-marius.md` log. Instruction cited; not verifiable (above) |
| Prompted by fetched or third-party text | No sign of it |

### Remaining gaps (not blocking; each is a strengthening and can be its own review-gated PR)

None is introduced by this PR. All four matter more after it, because the review gate becomes the only gate for rule files.

**N7. A conditional verdict line opens the gate.** `VERDICT_RE` accepts any line that begins with the approve verdict, whatever follows. Checked with the PR's script: a review whose last verdict line reads "…APPROVE once B1 is fixed" parses as APPROVE. The regex is unchanged from `main`. Fix: anchor the match to the end of the line.

**N8. An approval does not expire when the author pushes again.** The gate checks that an approving review file is among the PR's changed files. It does not check that the review is newer than the work.
- With auto-merge set at opening, the PR usually merges the moment the approval lands, so the window is small.
- It is open whenever CI fails for another reason after the approval, or auto-merge was refused. The author then pushes a "fix" and the PR merges with unreviewed changes to gated files.
- Fix, two parts: one sentence in CLAUDE.md ("a commit to a gated path after the approval needs a re-review"), and a CI check that no commit touching a gated path is newer than the last commit touching the approving review file.

**N9. Touching an old review still opens the gate.** B1's fix stops a *linked* old approval. A PR that changes one character in `finding-002-review.md` still counts that file (`counted_reviews` takes any changed `.md` under `docs/reviews/`). This is the stated limit "CI checks that a file exists, not who wrote it", but it is cheap to narrow: require the counted review to name the PR number, which the workflow can pass in.

**N10. The held-out lock checks the tag's name, not what it points to.** Agents create tags. A `predictions-x` tag on any commit satisfies CI. Suggested: CI checks that the tag is an ancestor of `main`; the rule-file checklist adds "the hypothesis that names the released document is merged at the tagged commit". Until S1 is done, such a tag can also be moved or deleted.

**Two stale lines, cosmetic.** The description's `ci.yml` bullet still says "taken from the base branch" (later corrected to `main` in the same description). The `for-marius.md` log lists #38 as merged before it is.

### Assessment

- The first review's three conditions for approval are met, and I verified each by running the code.
- The change does what the description says. The weakening is disclosed without softening.
- What is weaker after the merge, in one line: a rule change needs a second Claude instance and CI instead of a human; the instruction behind a weakening can be asserted but not checked by any reviewer. The `for-marius.md` log and Revert are the remaining human lever, and they work only if he reads the log.

Verdict: APPROVE
