# Independent review — H-A5-01 outcome and the Finding 001 addendum (PR #46)

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-14) that did not write H-A5-01, the benchmark code, the outcome file, the addendum or any other part of this PR. Required by `CLAUDE.md` → Merging (review-gated). It was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #46 at `347f0e5` against `main @ ab8a6c9`: `hypotheses/outcomes/H-A5-01.md`, the addendum of 2026-11-14 in `findings/001-yadiktu-null-test.md`, `experiments/A5.17/results/M1-hebrew-strong-verbs.{md,json}`, and the plan, research-notes and inbox changes.
- **Kind of review:** finding review (CLAUDE.md, Merging, item 3), because the PR changes a file under `findings/` and adds an outcome.
- **Rerun:**
  - the registered command, into a scratch directory;
  - an independent script that recomputes both tests without the runner's `HitTable` and `difference_test`;
  - the test suite (241 passed, 4 skipped);
  - the guardrail script from `main` (fails only for the missing review, as expected).
- **Not read (blinding respected):** KN Zg 57/58, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna.
- **Not checked:** di Mino 2026, Davis 2013 and Salgarella 2025 at first hand. The literature statements were checked against `docs/literature-survey-2026-10.md` only.

## Summary

The registered result stands. **Outcome A is correct**, the run follows the frozen protocol, and every table figure reproduces. Confidence: high.

Two sentences are wrong and are to be corrected before the merge (R1, R2). Neither changes a p-value, the outcome or the status of Finding 001.

## Requests

### R1. "397 of 1,000 random lexicons" should be 396
*Confidence: high (counted directly).*

- 396 of the 1,000 matched pseudo-lexicons have a hit rate at least as high as real Hebrew's. p1 = (1 + 396) / 1001 = 0.3966, as reported. 397 is the numerator after the added 1, not a count of lexicons.
- **Fix** in two places:
  - `hypotheses/outcomes/H-A5-01.md`, "In words": "397 of 1,000 random lexicons did at least as well as Hebrew";
  - `findings/001-yadiktu-null-test.md`, addendum: "397 of 1,000 random lexicons match at least as often".
- The research-notes entry, the inbox and the PR description do not carry the count, so they need no change.

### R2. Why the Finding 001 null is larger: collisions explain less than half of it
*Confidence: high for the figures (rerun); the mechanism I suggest in the last bullet is a hypothesis, not a finding.*

- The addendum says the pseudo-lexicons expand to about 744 forms "because random forms collide less often than real roots do", and rates the paragraph "Confidence: high (it is arithmetic on the lexicons …)".
- Rerun (Finding 001 null, seed 20261118, first 300 lexicons):

  | | Variants summed over the 502 forms | Distinct after expansion | Lost to collisions |
  |---|---|---|---|
  | Real Hebrew | 1,014 | 664 | 350 |
  | Finding 001 pseudo-lexicons (mean) | 1,064 | 744 | 320 |

- Of the difference of 80 forms, about 30 come from fewer collisions. About 50 come from the pseudo-forms having more variants each, before any collision.
- The 12% figure and everything that follows from it are right. Only the "because" clause is wrong in emphasis.
- **Fix:** state both parts, for example: "because a random form has more S/D/T variants on average than a real root (1,064 against 1,014 over 502 forms) and the variants collide less often (320 lost against 350)".
- A possible reason, as a hypothesis only: a form with two of S, D, T has four variants, and Semitic roots avoid two similar consonants in one root. The addendum need not explain it.

## The four checks of a finding review

### 1. Every claim follows from a registered outcome or is labelled exploratory — yes
- The decision (p1, p2, outcome A, batch of 1) is the registered rule applied without change. `hypotheses/H-A5-01.md` is untouched by the PR.
- Per-source rows, by-length rows, the Finding 001 null, the size table, random strings and degrees of freedom are placed under "Descriptive results (none of them decides anything)".
- **One claim rests on descriptive rows only:** that "Hebrew below random" in Finding 001 "came from the null's size, not from Hebrew". The PR supports it by the same deficit on Greek words. I tested it directly (next section, table 2). It holds.
- The limits are stated where they belong: no known positive at Tier 1, L1 only, Hebrew verbs only, an approximate encoding of the paper's licences, and "does not say that Linear A is not Semitic".

### 2. The numbers, by rerunning the code — reproduce, bar R1
- **Registered command:** output identical to the committed `.md` and `.json` except the commit stamp (`347f0e5` in my run, `ab8a6c9` in the PR's). `src/`, `tests/`, `data/` and `tools/` do not differ between `bbe9c69`, `ab8a6c9` and the PR head, so "unchanged code" is correct.
- **Order of events:** PR #45 merged at 16:28:51 UTC; the outcome commit is dated 16:33:03 UTC and its output is stamped with the merge commit. I cannot verify "run once"; the run is deterministic, so it does not matter for the figures.
- **Independent recomputation** (own loop over `method.hits`; leave-one-out written out, not the algebraic shortcut):

  | Claim | Rerun |
  |---|---|
  | 414 eligible sign-groups; control 902 of 918 | 414; 902 of 918 |
  | Real Hebrew matches 321 (0.775) | 321 / 414 = 0.7754 |
  | Pseudo-lexicons 0.769, standard deviation 0.017 | 0.7691, 0.0169 |
  | p1 = 0.397 | 396 at or above; 0.3966 |
  | Control 0.532 against 0.512, p = 0.064 | 0.5322, 0.5121, 0.0639 |
  | Control at Linear A's lengths 0.684 against 0.660 | 0.6837, 0.6601 |
  | Difference −0.017, p2 = 0.840 | −0.0174; 840 at or above; 0.8402 |
  | Test 1 needed an excess of about +0.03 | 331 matches needed for p1 ≤ 0.05: +0.0304 |
  | Test 2 needed a difference of about +0.03 | 95th percentile of the null's difference: +0.031 |
  | Matched pseudo-lexicons: 664 after expansion, 457 before | all 1,000 exactly 664; mean 457.3 |

- Per-source, by-length, stability, size, random-string and degrees-of-freedom figures in the outcome file match the generated output line by line.

- **The size claim, tested** (reviewer's check; pseudo-lexicons only, 300 each, exploratory, decides nothing):

  | Null | Forms after expansion | Linear A | Greek control |
  |---|---|---|---|
  | Finding 001 (overall letter frequencies, 502 forms) | 744 | 0.803 | 0.560 |
  | The same letter model, cut to 664 after expansion | 664 | 0.780 | 0.538 |
  | Matched (letter frequencies per position, 664) | 664 | 0.769 | 0.512 |
  | Real Hebrew | 664 | 0.775 | 0.532 |

  - Matching the size alone, with Finding 001's own letter model, takes real Hebrew from 0.028 below the null to 0.004 below on Linear A, and from 0.029 to 0.006 below on the control. Both are inside the null's spread (0.017 and 0.013). So the addendum's claim is right: the deficit was the null's size.
  - Outcome A does not depend on the letter model: under either size-matched null, real Hebrew is within noise on Linear A.

### 3. Circularity — none that affects the result
- **Held-out data:** 0 of the 478 documents the loader returned are on the held-out list. The run used `load.witnesses()` with the default training split.
- **Value-converted fields:** the inputs are L1 values from sign IDs. `transliteratedWords` is not parsed.
- **Null built from the real lexicon:** the pseudo-lexicons take their size, lengths and letter frequencies from the Hebrew lexicon. That is the purpose of a matched null, not a circle.
- **Control:** the Linear B words come from the NeuroDecipher list, which is independent of the Hebrew lexicon and of Linear A. Linear A and the control share the Linear B sign values, as the layer statement says.
- **Design after seeing data:** the matched null and Test 2 were fixed after control-side figures were seen, and Finding 001's Linear A figures were known. Both are disclosed in the frozen file, and the hypothesis is exploratory. Knowing the control's excess (+0.024) in advance could only make outcome C harder to reach.
- **The addendum does not use its own result as support for a value or a reading.** It makes no claim about sign values.

### 4. Literature — consistent with the survey
- The addendum calls the Semitic proposals (Gordon, Best, di Mino 2026) fringe and "no match demonstrated with any family" the consensus (Davis 2013; Salgarella 2025). That is what survey §6.5 and its consensus table say.
- It claims agreement with the consensus "only in the narrow sense that one proposed demonstration fails". That is the right size of claim.
- "Luo, Cao & Barzilay 2019" matches `DATA_SOURCES.md`. The open point on where that word list comes from is carried in the research-notes entry.
- The original script does read PA3 as P and ZU as S (`experiments/finding-001/original/nulltest.py`), as the addendum says.

## Rules
- `research-notes.md`: one entry appended, nothing earlier edited.
- No rule file, no held-out list and no code is touched.
- The plan checkbox A5.17 stays open with an annotation; the reason is given.
- The two new follow-ups in `docs/for-marius.md` are the two points added under M3 of the H-A5-01 re-review.
- The PR description starts with the review-gated line and names this file.

## Non-blocking notes
- **"about twelve more matched sign-groups"** (outcome file, Power). Test 1 needed 331 matches. That is 10 more than Hebrew got (321) and about 12.6 more than a random lexicon gets on average (318.4). Say which.
- **"Hebrew's small edge over random lexicons is larger on Greek words"** (outcome file and addendum). The edge is relative to the matched null. Under the size-matched null with overall letter frequencies (table above), Hebrew is slightly *below* random on both inputs. The sentence is correct as a description of the registered test; "over the matched pseudo-lexicons" would say so.
- **"table above: lexicon size"** (addendum, Limits). In the finding the size figures are a sentence under the table, and the new size table is in the results file.

**Status:** R1 and R2 open.

Verdict: CHANGES REQUESTED

---

## Re-review

Fix R1 and R2 in the PR. A reviewer then appends a re-review below this line.

### Re-review 1 (2026-11-17)

- **Reviewer:** a separate Claude instance (fresh subagent) that wrote neither this PR, the fix commit, nor the first review above. It was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #46 at `fd76b03` ("fix R1 and R2"), against the first review at `2b6ba4e` and `main`.
- **Not read (blinding respected):** KN Zg 57/58, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna.

#### R1 — resolved
*Confidence: high (recounted with my own loop over `M1.match`, not with `HitTable` or `compare`).*
- 414 eligible sign-groups; real Hebrew 321 hits (0.7754); matched null mean 318.43 (0.7691).
- **396** of the 1,000 matched pseudo-lexicons (seed 20261114) score at or above Hebrew; p1 = 397/1001 = 0.3966.
- The outcome file and the addendum now say 396. The remaining "0.397" occurrences are p1 itself, which is correct.
- Power wording: 331 hits are needed for p1 ≤ 0.05 (recomputed). That is 10 more than Hebrew's 321 and 12.6 more than the null mean of 318.4. "about 13 more … (318)" is right.

#### R2 — resolved
*Confidence: high for the figures (rerun); the mechanism stays a hypothesis, and the PR labels it so.*
- Rerun, Finding 001 null (seed 20261118, first 300 lexicons, `M1.variants` summed per form, then the union):

  | | Variants over 502 forms | Distinct | Lost to duplicates |
  |---|---|---|---|
  | Real Hebrew | 1,014 | 664 | 350 |
  | Finding 001 null, mean | 1,063.8 | 743.5 | 320.3 |

  Over all 1,000 lexicons the distinct mean is 744.1.
- The addendum now names both parts (about 50 from more variants per form, about 30 from fewer duplicates). Both figures match.
- The correction to the earlier research-notes entry is made in a new entry that references the old one. `research-notes.md` has only additions against `main`. That is what the append-only rule requires.

#### Non-blocking notes from the first review — handled
- "twelve more sign-groups" now says which comparison (see R1).
- The "edge" sentence now says "over the matched pseudo-lexicons" (outcome file) and "over the size-matched pseudo-lexicons" (addendum). In the addendum, the only size-matched null is the one in its table, so the wording is unambiguous there.
- The "table above" pointer now names the sentence under the Results table and the size table in the results file.

#### Nothing else changed
- The fix commit touches only `findings/001-yadiktu-null-test.md`, `hypotheses/outcomes/H-A5-01.md` and `research-notes.md`, and only in the places listed above. `hypotheses/H-A5-01.md`, code, data and rule files are untouched.
- No p-value, outcome label or status changes. Outcome A and "Status unchanged: NEGATIVE for the method" stand.
- Test suite: 241 passed, 4 skipped. The guardrail script from `main` fails only because no review here ends in APPROVE, as expected before this re-review.
- The first reviewer's report is recorded as a PR comment (2026-11-14 16:41 UTC). I have not seen the original report, so I cannot confirm that the comment is unedited.

**Status:** R1 and R2 resolved. No open requests.

Verdict: APPROVE
