# Independent review — H-A5-02 outcome (PR #50)

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-17) that did not write H-A5-02, the benchmark code, the outcome file, the descriptive script or any other part of this PR. Required by `CLAUDE.md` → Merging (review-gated). It was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #50 at `176854e` against `main @ 6ca24d5`: `hypotheses/outcomes/H-A5-02.md`, `experiments/A5.17/h_a5_02_no_two_letter.py` and its output, `experiments/A5.17/results/H-A5-02-M1-english-verbs.{md,json}`, `batch.{md,json}`, and the changes to `docs/benchmark.md`, `docs/for-marius.md`, the plan and `research-notes.md`.
- **Kind of review:** an outcome under `hypotheses/`, reviewed against both lists: the hypothesis items as they bear on the run (did the run follow the frozen file), and the finding items (claims follow from the registered outcome, numbers rerun, circularity, literature).
- **Rerun:**
  - the registered command, into a scratch copy of the results directory as it stood on `main @ 6ca24d5`. The four generated files are byte-identical to the committed ones, except for the commit hash in the provenance (`176854e`, the checkout, instead of `6ca24d5`). That is expected and not an error;
  - the descriptive script `h_a5_02_no_two_letter.py`. Its output is byte-identical to the committed JSON;
  - an independent script (scratch, not committed) that recomputes Test 1, the control and Test 2 (length re-weighting and leave-one-out included), with and without two-letter forms, by calling `M1.match` directly. It does not use `HitTable`, `compare` or `difference_test`. Every figure agrees to the fourth decimal (table below);
  - the test suite: 267 passed, 4 skipped;
  - `git diff 007c647 6ca24d5 -- src tests` is empty, as the outcome file says. This PR changes nothing under `src/`, `tests/`, `tools/`, `.github/` or `data/`.
- **Not read (blinding respected):** KN Zg 57/58, `data/heldout.txt`, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna.

## Summary

The registered result stands. **Outcome B (Test 1 only) is the label the decision rule gives**, the registered prediction (p2 > α) is met, the run followed H-A5-02 with no deviation, and every figure I checked reproduces. Confidence: high.

I have no requests that block the merge. There are four notes (N1–N4). None changes a p-value, the outcome or the reading.

## Checks

### The run against the frozen hypothesis
- H-A5-02 was merged at `6ca24d5` (2026-11-17 19:02:28 UTC). The outcome commit is `176854e` (19:06:57 UTC). The registered command takes about 1.5 minutes here, so the times fit a single run after the merge. *Confidence: high that the order is right; I cannot verify from the repository that the command ran only once. That rests on the author's statement.*
- Code named in the hypothesis (`007c647`) and the code at the run (`6ca24d5`) are identical under `src/` and `tests/`.
- Seeds 20261114 (null) and 20261115 (A1.14 harness), 1,000 pseudo-lexicons, α = 0.05, as registered.
- **Decision rule:** `batch.label` gives B1 when p1 ≤ α < p2, whatever the adjusted pair p. That matches H-A5-01's table ("exactly one of p1, p2 is ≤ α"). BH over (0.840, 0.754): this pair's adjusted p = min(2 × 0.754, 0.840) = 0.840, as reported. H-A5-01 stays A. Batch count 2, as reported.
- **Prediction:** "p2 > α, that is outcome A, or B with p1 ≤ α only". p2 = 0.754: met. The outcome file reads the result exactly as H-A5-02 fixed in advance for "B with p1 ≤ α only".
- **The registered descriptive check** is implemented as registered: two-letter forms are removed after expansion (`M1.prepare`), from the real lexicon and from the same 1,000 pseudo-lexicons (drawn with the unmodified M1, as in the run). The sizes that review note N7 of PR #49 asked for are reported beside the check, with the direction of the leftover bias.

### Numbers (independent recomputation)

| Quantity | Outcome file | Independent |
|---|---|---|
| Linear A: n, real, false-positive rate | 414, 0.705, 0.641 | 414, 0.7053, 0.6407 |
| Pseudo-lexicons at least as good | 8 | 8 |
| p1 | 0.009 | 0.0090 |
| SD of pseudo-lexicon hit rates | 0.029 | 0.0291 |
| Control: excess, p | +0.070, 0.002 | +0.0697, 0.0020 |
| Control at Linear A's lengths | +0.081 | +0.0810 |
| Test 2: D, p2 | −0.016, 0.754 | −0.0164, 0.7542 |
| Without two-letter forms: forms real / null mean | 936 / 953.3 | 936 / 953.3 |
| Without: Linear A excess, p1 | −0.007, 0.581 | −0.0068, 0.5814 |
| Without: control excess, p | +0.032, 0.139 | +0.0316, 0.1389 |
| Without: D, p2 | −0.032, 0.889 | −0.0322, 0.8891 |

Arithmetic in the prose also checks: 0.705 × 414 = 292 sign-groups; 0.065 × 414 ≈ 27; log2(953.3 / 936) = 0.026 doublings, × 0.15–0.17 ≈ 0.004 (the N7 estimate). The per-source, by-length, Finding 001 null, stability, size-curve, random-string and degrees-of-freedom figures in the outcome file match the generated report. The comparison figures for Hebrew (SD 0.017, 4.2% coverage, below the Finding 001 null) match `hypotheses/outcomes/H-A5-01.md`.

### Claims follow from the registered outcome or are labelled
- The outcome label, p-values and "prediction met" follow from the registered rule.
- "English's advantage on Linear A is carried by its two-letter forms" rests on the registered descriptive check and is labelled as decided by nothing. The mechanism is labelled as the author's reasoning (rule 5). That is adequate.
- Statements about Indo-European root shape are marked as untestable from this run.
- "This outcome says nothing about the language of Linear A" is correct and present.

### Circularity
- The lexicon comes from WordNet 3.0 and CMUdict, which are independent of any Aegean source. Linear A sign-groups are read in conventional Linear B values (L1, stated). The control comes from the NeuroDecipher Linear B–Greek data. No value or reading used here was derived from the lexicon under test, so I see no circularity. The one structural link, English and Greek both being Indo-European, is disclosed in the hypothesis before the run and in the outcome. *Confidence: high.*

### Literature
- The outcome makes no claim about Linear A and cites none. Its general lesson, that a lexical-match count needs a chance baseline matched to the lexicon's phonotactics and form lengths, agrees with the standard literature on chance resemblance in long-range comparison, for example Ringe 1992 (*On Calculating the Factor of Chance in Language Comparison*) and Kessler 2001 (*The Significance of Word Lists*). I checked those references from memory, not at first hand. Nothing in the outcome disagrees with them. *Confidence: medium-high; not a blocker.*

## Notes (non-blocking)

**N1. "Test 2 would have needed a difference of about +0.044" uses the two-sided bound.** *Confidence: high (recomputed).* +0.044 is the 97.5th percentile of the pseudo-lexicons' leave-one-out differences. Test 2 is one-sided at α = 0.05, so the threshold is the 95th percentile, **+0.037** (with two-letter forms removed: +0.043 rather than +0.051). The reading does not change: D = −0.016 is far below either value. H-A5-01's outcome uses the same convention ("about +0.03"). Suggest that a later outcome, or the revised protocol, report the 95th percentile when it speaks of the size needed.

**N2. "Test 1 alone gives false positives" (outcome, "What follows"; `docs/benchmark.md`; research-notes) generalises from one lexicon.** The run shows that Test 1 *can* give a false positive at p = 0.009, stably across sources and resampling. It does not show how often. "Can give" would be more exact. The practical rule drawn from it ("never quote a Tier 1 result from Test 1 alone") holds either way. Research-notes is append-only, so any change belongs in a later entry if the author wants one.

**N3. The control's residual excess without two-letter forms (+0.032, p = 0.139) is not significant on its own.** The outcome says "about half of English's advantage survives" on the control, and it does not over-read that figure. I note it only so that nobody later reads "English differs from its pseudo-lexicons in more than form length" as a measured result: at p = 0.139 it is a point estimate, not a demonstrated difference.

**N4. `docs/for-marius.md`:** the new item is followed by a blank line, which splits the bulleted list under "Small things an agent will do without asking" into two lists. This is cosmetic. On the substance: listing the length-stratified protocol there, rather than as a decision for Marius, seems right to me. It is a new hypothesis file, review-gated, and it leaves H-A5-01 unchanged, so it neither weakens a guardrail nor sets a new direction.

## Process
- First line of the PR description: "**Review-gated: `docs/reviews/H-A5-02-outcome-review.md`**", which is this file.
- No rule file, held-out file or enforcement code is touched. `research-notes.md` and the plan change only by appended lines.
- Before this review, CI (`test`) failed. I take that to be the missing review, as expected for a review-gated PR.

Verdict: APPROVE
