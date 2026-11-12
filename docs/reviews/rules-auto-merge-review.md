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
