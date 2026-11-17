# Independent review — H-A5-02 (Tier 1, pair 2: M1 × English verbs), PR #49

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-17) that did not write H-A5-02, the English lexicon loader (PR #48), the benchmark code or any part of this PR. Required by `CLAUDE.md` → Merging (review-gated). Given the PR number and the fixed review prompt only.
- **Reviewed:** PR #49 at `f230103` against `main @ 007c647`: `hypotheses/H-A5-02.md`, the plan change-log line, the research-notes entry; and the code the file names (`src/aegean/benchmark/{lexicons,nulls,m1,batch}.py`), read against Part 1 of `hypotheses/H-A5-01.md`, its outcome file and both earlier reviews.
- **Rerun:** the test suite (267 passed, 4 skipped); the guardrail script from `main` (its only complaint: no review file in the PR, as expected); every lexicon-side figure in the file (table below); 1,000 matched pseudo-lexicons for the English lexicon with the protocol seed, lexicon side only.
- **Not done, on purpose:** no hit rate of the English lexicon or of any pseudo-lexicon was computed, on Linear A sign-groups or on the Greek control. Both are part of the registered run. No Linear A data and no held-out material were read.
- **Not checkable from the repository:** the statement that no English hit rate was seen before registration. It is consistent with what is there: `experiments/A5.17/results/` holds only the H-A5-01 files and a one-pair `batch.json`.

## Summary

The file is short, cites the protocol correctly, states its prediction and how each outcome will be read before the run, and is candid that English, being Indo-European, is a weak check. Every figure it gives reproduces. One statement in "What I already know" is false, and it is the one that predicts how the lexicon's length profile acts on the tests. Because the file is immutable after the merge and this pair exists to check Test 2's assumption, it must be corrected first.

## Required change

### R1. The matched null does not have the English lexicon's lengths: it is short of two-consonant forms
*Confidence: high (measured on all 1,000 pseudo-lexicons of the protocol seed; lexicon side only).*

- The file says (under "Expectation, not a result"): "The matched null has the same lengths, so this should not by itself move either test."
- `nulls.matched_lexicon` draws each form's length from the real forms, but rejects a form already drawn. There are at most 11 × 10 two-letter forms under English's positional frequencies, with uneven weights, so two-letter draws collide often and are thrown away more often than longer ones. The realised pseudo-lexicons are therefore shifted towards longer forms. Hebrew had no two-consonant skeletons, so H-A5-01 never met this.
- Measured (seed 20261114, the protocol's 1,000):

  | | Real English | Matched pseudo-lexicons: mean (95%; min–max) |
  |---|---|---|
  | Two-consonant forms before expansion | 71 of 502 | 50.2 (40–59; 37–65) of about 455 |
  | Four-consonant forms before expansion | 228 | 231.4 (213–250) |
  | Two-letter forms after M1's interchanges | 79 of 1,015 | 61.7 (52–70; 47–76) of 1,015 |

  The real lexicon has more two-letter forms, as M1 sees it, than every one of the 1,000 pseudo-lexicons. The total of 1,015 is matched exactly, so the null makes up the difference with three- and four-letter forms.
- Why it matters (argument, not a measurement, rule 5): under M1 a two-letter root matches any sign-group with a two-sign core after an allowed prefix or suffix is removed, and two-sign cores are where almost everything matches (H-A5-01 by length: 0.963 and 0.933 at two signs). A surplus of the most permissive forms should raise the English lexicon's hit rate over the null on any input. That favours a small p1 on Linear A and a positive excess on the control, whatever the relation of English to Linear A. Whether Test 2 cancels it depends on whether the gain is the same size on both inputs, which is exactly the assumption this pair is meant to check. The length re-weighting in Test 2 is by sign count, not by how many two-consonant readings a sign-group admits, so it does not remove the effect by construction.
- So the expectation stated in the file has the wrong premise, and the direction it predicts ("should not move either test") is probably wrong for Test 1. This bears on the prediction (outcome A) and on how outcome B with p1 ≤ α only, and outcome C, will be read.
- **Fix in the file** (no change to the protocol, its constants or the decision rule is asked for):
  1. Replace the sentence with the measured figures above, labelled as seen through this review.
  2. State in advance the expected direction: the surplus of two-consonant forms favours the real lexicon in Test 1 on any input; if Test 2 does not cancel it, outcome B (second or third kind) or C is the false positive the pair is designed to catch; outcome B with p1 ≤ α only is then the expected result of this artefact, not of anything about English.
  3. Revisit the stated prediction in that light (keeping A is the author's call, but say why).
  4. Either keep the lexicon as merged in PR #48 and say so, or change the lexicon (a new conversion needs its own plain PR and the file must name it). Changing it after seeing this figure is design knowledge; if chosen, disclose it.
- Optional, deciding nothing: a pair-specific descriptive row in the outcome file, the English lexicon's hit rate by lexicon-form length (or with two-consonant forms removed from the real and the pseudo-lexicons alike), so the size of the artefact can be read off. If added, name it in the file now.

## The four required checks

### 1. Null model — the protocol's, adequate except for R1
- All 1,000 matched pseudo-lexicons reach exactly 1,015 forms after expansion (checked on all 1,000; real 502 skeletons → 1,015). They average about 455 forms before expansion against the real 502, as expected, since random forms expand more (fewer collisions among variants).
- One seeded stream for Linear A and the control (Part 1, unchanged). The Greek control is present.
- The null's length profile differs from the real lexicon's (R1). This is a property of the protocol's generator that only bites on a lexicon with short forms; it is not a deviation from Part 1, and the protocol is not to be changed in this PR.
- The control argument (English is Indo-European but not "close to Greek") is acceptable. A few English verbs of Greek origin may be in the 502 (the -ize type); they would need Mycenaean counterparts among 902 economic-text words to matter, so negligible. My reasoning, not checked.

### 2. Power check — passes
- Smallest attainable p, both tests: 1/1001 ≈ 0.000999 < α.
- Batch arithmetic checked: with two pairs and H-A5-01's pair p of 0.8402 (`batch.json`), Benjamini–Hochberg (the correction that keeps the expected share of false discoveries in a batch below a set level) gives this pair min(2p, 0.8402) when p < 0.8402, and leaves H-A5-01 at 0.8402. Outcome C needs a raw pair p ≤ 0.025; attainable. Correct.
- The runner reads H-A5-01's committed results file and `batch.json`, so the batch of 2 the file describes is what the code will apply (`batch.records`, `batch.admit`; the H-A5-01 record is present with `pair_key 9c8b2d5110d22509`).
- The file says the pseudo-lexicons' spread may differ and the outcome file reports it. With 1,015 forms, hit rates will be nearer the ceiling than Hebrew's (H-A5-01: 0.808 at the Finding 001 null's real size, 0.896 at twice the size), which may narrow the spread. My expectation, not a result; reporting it, as promised, is enough.

### 3. Decision rule and batch count — sound
- Decision rule is Part 1's; A and the first two kinds of B on raw p1 and p2, C only after the batch correction. The file's statement that H-A5-01's A cannot change is right (`batch.label` returns A before looking at the adjusted value).
- Batch: pair 2 of 2; running count of A5 hypotheses 2. No other A5 hypothesis exists under `hypotheses/`.
- `- **Protocol:** H-A5-01` is present in the form `batch.PROTOCOL_LINE_RE` requires; the `Type:` line is exploratory and does not match `load.CONFIRMATORY_RE` (the held-out split stays closed). Rule 10 satisfied.
- The run command uses options the runner has (`--method M1 --lexicon english-verbs --protocol H-A5-02`; `english-verbs` is in `lexicons.REGISTRY`).
- The pre-fixed reading of each outcome is good practice and consistent with the decision rule. With R1 fixed it will also say which reading the known artefact predicts.

### 4. "What I already know" — complete apart from R1
- Lists the H-A5-01 result, the informal look at H-A5-01's matches, and the lexicon-side figures, and states what was not seen. Every listed figure reproduces (table below).
- The one false statement is R1's. After this review the author also knows the figures in R1's table; they go into the file as "seen through the independent review", as H-A5-01 did.
- Small addition, not required: the ranking covered 8,429 WordNet verb lemmas (`last_verb_taken` and `skipped` in the loader's metadata), which completes the skip counts given.

## Figures rerun (lexicon side, `f230103` code, fetched data with hashes verified by the loaders)

| Claim in the file | Rerun |
|---|---|
| 502 skeletons; the 502nd from *hurtle* | 502; `('hurtle', 2)` |
| Lengths 71 / 203 / 228 (Hebrew 0 / 488 / 14) | 71 / 203 / 228 (Hebrew 0 / 488 / 14) |
| Letters R 0.20, S 0.15, P 0.13, K N T 0.11, D 0.09, M 0.05, H W 0.02, J 0.01 | R 0.197, S 0.153, P 0.135, N 0.113, T 0.108, K 0.105, D 0.086, M 0.053, W 0.022, H 0.017, J 0.011 |
| Adjacent identical letters 0.100 (Hebrew 0.139) | 0.100 (0.139) |
| 1,015 forms after expansion (Hebrew 664) | 1,015 (664) |
| 103 of the 502 skeletons also Hebrew skeletons | 103 |
| Skipped: 6 no pronunciation, 217 length, 496 duplicates | 6, 217, 496 |
| Matched pseudo-lexicons drawn to 1,015 forms | all 1,000 at 1,015 |

Script: `/tmp` only, not committed; it imports `aegean.benchmark.{lexicons,nulls,m1}` and computes nothing on any sign-group.

## Notes (no change required)

- **N1. Other files.** `research-notes.md` is appended to only; the plan gets one change-log line and A5.17 stays open, which is right. No rule file is touched; nothing I can see was prompted by fetched content. The PR description's first line names this file.
- **N2. The weak-check caveat** (English and Greek share Indo-European root shapes, which would lower D) is reasoning, stated as such, and points to a non-Indo-European pair later. Agreed. R1 is an effect in the other direction, through the null rather than through the language.
- **N3. Rule 5.** Everything in R1 after the measured table, and the notes on ceiling and Greek loanwords, is my reasoning, not a result.

## Re-review

Fix R1 in the PR. A reviewer then appends a re-review below this line.

Verdict: CHANGES REQUESTED
