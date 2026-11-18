# Independent review — H-A5-09 (Tier 1 protocol revision 2, bigram-matched null) and H-A5-10 to H-A5-14, PR #63

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-19). I did not write H-A5-09 to H-A5-14, the bigram null (PR #61) or any part of this PR. Required by `CLAUDE.md` → Merging (review-gated). I was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #63 at `51cd7ab` against `origin/main @ 1175f93`: `hypotheses/H-A5-09.md` to `H-A5-14.md`, the plan change-log line and the research-notes entry. Read against `hypotheses/H-A5-01.md` and `H-A5-03.md` (Part 1), the H-A5-01 to H-A5-08 outcomes and reviews, PR #61 (`d5eeb6d`: `nulls.bigram_matched_lexicon`, `batch.PROTOCOLS`, `tier1.matched_lexicons`, tests), `docs/benchmark.md`.
- **Rerun:**
  - `pytest tests/test_benchmark_batch.py tests/test_benchmark_inputs.py tests/test_guardrails.py`: 41 passed;
  - `tools/check_guardrails.py origin/main`: the only failure is the missing review, as expected before this file;
  - `batch.check_registered` in a scratch clone with `main` set to the PR head: H-A5-09 to H-A5-14 all map to protocol H-A5-09; H-A5-03 to H-A5-08 still map to H-A5-03, which accepts no other IDs;
  - every figure quoted from earlier runs, against the committed results JSON (below);
  - the lexicon-side validation of the bigram null, with a scratch script (not committed): the first 100 pseudo-lexicons of the registered stream (`random.Random(20261114)`, drawn in sequence, as the runner draws them), for both nulls and all six (method, lexicon) pairs.
- **Deliberately not done:** I computed no hit rate of any lexicon, real or pseudo, under the bigram null, on Linear A or on the Greek control. I read no held-out material. Linear A and the control were not loaded at all; everything I computed is lexicon-side.

## Summary
The registration is mostly sound: the null is implemented as described, the power check and the batch arithmetic are right, the runner enforces the closure of H-A5-03, the disclosures are honest (all six pairs are declared not blind), and every earlier figure quoted reproduces. Two changes are needed before merge, both cheap, and both in a file that becomes immutable on merge:

- **R1.** The bigram null does not only *add* adjacent-letter matching to H-A5-03's null; it also *gives up* H-A5-03's matching of letter frequencies at each position after the first. I measured this. H-A5-09 does not say so, and its pre-fixed calibration reading attributes any change between the two nulls to letter co-occurrence alone. That reading also overstates its conclusion and leaves the mixed case open.
- **R2.** The validation figures cite "research-notes 2026-11-18", but no research-notes entry contains them.

## The four required checks

### 1. Null model: implemented as described, but one material property is undisclosed (R1)
*Confidence: high (code read; lexicon side measured).*
- `nulls.bigram_matched_lexicon` does what Part 1, point 1 says. It reads first letters per length and next letters pooled over lengths and positions, both from the real lexicon's pre-licence forms. A draw that hits a letter with no successor is discarded. Forms are filled length by length to the exact expanded-form count, duplicates are rejected, and expansion is length-preserving (checked). `tier1.matched_lexicons(kind="bigram")` draws K = 1,000 in sequence from seed 20261114, and `batch.PROTOCOLS["H-A5-09"]` maps to it.
- **Lexicon-side figures reproduce.** Mean over the first 100 registered draws:

  | Pair | Overlap, stratified | Overlap, bigram | TV bigrams, stratified | TV bigrams, bigram | **TV positional, stratified** | **TV positional, bigram** |
  |---|---|---|---|---|---|---|
  | M1 × Hebrew | 0.686 | 0.680 | 0.163 | 0.115 | 0.067 | 0.094 |
  | M1 × English | 0.411 | 0.471 | 0.257 | 0.110 | 0.079 | 0.111 |
  | M1 × Turkish | 0.483 | 0.440 | 0.190 | 0.128 | 0.081 | 0.176 |
  | M2 × Hebrew | 0.626 | 0.630 | 0.140 | 0.104 | 0.063 | 0.091 |
  | M2 × English | 0.344 | 0.417 | 0.235 | 0.101 | 0.068 | 0.105 |
  | M2 × Turkish | 0.426 | 0.383 | 0.171 | 0.121 | 0.078 | 0.168 |

  - Overlap is the share of the real lexicon's expanded forms that also occur in the pseudo-lexicon's expanded forms.
  - TV is the total-variation distance between real and pseudo-lexicon distributions: of letter bigrams, and of (length, position, letter) triples.
  - The file's ranges hold: overlap 0.38–0.68 (bigram) against 0.34–0.69 (stratified); bigram-distribution TV 0.10–0.13 against 0.14–0.26.
- **What the file does not say (R1).** The positional TV rises from 0.06–0.08 (stratified) to 0.09–0.18 (bigram). The stratified null's 0.06–0.08 is close to the floor that finite sampling sets, because positions are matched by construction. Turkish more than doubles (0.081 → 0.176; 0.078 → 0.168 under M2). This is expected: after the first letter, a pooled first-order chain reproduces transitions, not positional frequencies (for example, which letters end forms of a given length). H-A5-09 says that "Everything in H-A5-03, Part 1 holds without change, except the decision null". It then lists what the new null does not match: "co-occurrence beyond adjacent letters, and position-specific transitions". It does not say that the positional letter frequencies, which H-A5-03 explicitly matched ("positional letter frequencies are matched"), are now only partly matched.
- **Why it matters.** The motivation of the revision, and the calibration reading fixed in advance, treat the change from H-A5-03's null to this one as a change in one factor, adjacent-letter co-occurrence. It is a change in two: co-occurrence gained, positional frequencies partly lost. The sign of the second factor's effect on hit rates is unknown (it depends on the target sign-groups' structure, not only on the lexicon). So neither outcome of the calibration reading isolates co-occurrence:
  - if M1 × English and M1 × Turkish still beat the null on Greek words, the co-occurrence account may still be right, with the loss of positional matching creating an advantage of its own;
  - if they no longer do, the loss of positional matching may be what removed it.

### 2. Power check: correct
*Confidence: high (recomputed).*
- n = 414 / 902 (M1) and 378 / 881 (M2), as in the committed H-A5-03 to H-A5-08 results (`control.n` = 902 and 881).
- K = 1,000, so the smallest attainable p is 1/1001 for both tests. With m = 6, a single small pair p is adjusted to at most 6p: a raw 0.0083 gives 0.0498, and 1/1001 gives 0.006. "Outcome C needs a raw pair p ≤ 0.0083; attainable" is right. The 50-pair ceiling (`batch.MAX_PAIRS`) is far off.
- Not a defect, but worth stating in the outcome files: the pseudo-lexicons share 38–68% of the real expanded forms (Hebrew about two-thirds under both methods). Test 1 therefore contrasts the real lexicon with noise only through the remaining forms, and an A is weak evidence for that reason as much as for any other (N3).

### 3. Decision rule and batch count: correct
*Confidence: high.*
- The decision rule is H-A5-03's (H-A5-01's table and BH at q = 0.05), unchanged; only the null and the batch change. `batch.label` and `batch.bh_adjust` implement it as stated.
- Own batch `batch-H-A5-09`, six pairs; `batch.records` keeps protocols apart, so the six earlier H-A5-03 runs of the same pairs do not enter it and `admit` raises no "pair already run" clash. Results files get new stems (`H-A5-1x-…`), so nothing is overwritten.
- H-A5-03 is closed to new pairs (enforced since PR #61), as the PR #55 re-review (M1) and the PR #60 review (N8) asked. The file adds the rule that any later revision must close H-A5-09.
- Point 4 (least favourable of all outcomes, A < B < C) generalises H-A5-03's two-protocol rule correctly. Each pair file states its earlier runs and their outcomes, which is what the PR #60 review N8 asked for.
- Running count 14 (H-A5-01 to H-A5-14): correct.
- Run commands: the runner's `--protocol` takes the hypothesis ID, and each file gives its own ID. Correct.

### 4. "What I already know": complete in substance; all quoted figures reproduce
*Confidence: medium-high. Read against the repository; the author's session is not visible to me.*
- Checked against the committed results JSON:
  - M1 × Hebrew: Linear A excess +0.006 (H-A5-01) and +0.003 (H-A5-03);
  - M1 × English: p1 = 0.009 (H-A5-02), 0.288 (H-A5-04); control +0.070 and +0.033, p = 0.015;
  - M1 × Turkish: p1 = 0.100; control +0.032, p = 0.017;
  - M2: p1 0.946 (Hebrew, excess −0.032), 0.716, 0.671; control +0.019 (p = 0.139) and −0.003 (p = 0.589).

  All right.
- The six pairs are declared not blind, and the lexicon-side figures of the null are listed. I found nothing in the repository that was seen and not listed, except what this review now adds (the positional figures above), which the outcome files should list as seen through the review.
- Two small gaps, non-blocking (N1).

## Required changes

- **R1. Disclose the positional trade-off, and fix the calibration reading accordingly** (H-A5-09, Part 1).
  1. Under "What it does not match", add that the bigram null, unlike H-A5-03's, does not match letter frequencies at positions after the first. Give the measured figures: positional TV 0.09–0.18 against 0.06–0.08, from this review. Add that the comparison with H-A5-03's calibration row therefore changes two things at once.
  2. Reword the reading fixed in advance. As written:
     - it concludes "letter co-occurrence is not the explanation", which is stronger than the evidence could be even without the confound. The null matches adjacent letters only, so a persisting advantage would show at most that adjacent-letter co-occurrence does not account for all of it;
     - it fixes no reading when one of the two lexicons is at p ≤ 0.05 and the other is not;
     - it rests on a p-value threshold only. The excess beside H-A5-03's +0.033 / +0.032 is the more informative quantity.

     A possible wording:

     > If both M1 × English and M1 × Turkish still beat the null on Greek words at p ≤ 0.05, adjacent-letter co-occurrence does not account for the whole advantage. If both are above 0.05, that is consistent with it being part of the advantage. Either reading is qualified: this null also gives up H-A5-03's positional matching after the first letter, an effect of unknown sign. If the two lexicons disagree, no reading is fixed. Each case is reported with the excess beside its H-A5-03 value.

  - Alternatively, the author may make the chain position-aware, so that the revision changes one factor. That is a code change (a plain PR) and a different null, and I do not require it.
- **R2. Fix the citation of the validation figures** (H-A5-09, Part 1, "Known-script validation").
  - "research-notes 2026-11-18" points to nothing: no 2026-11-18 entry mentions the bigram null's overlap or TV figures. They appear only in `docs/benchmark.md` (PR #61), and no committed script produced them (no seed recorded; CLAUDE.md, Code conventions).
  - Cite `docs/benchmark.md` (PR #61) and this review instead. This review reproduces the ranges on the first 100 registered draws (seed 20261114, in sequence).
  - Committing the validation script with its seed in a later plain PR is suggested, as the PR #60 review (N5) suggested for the M2 calibration.

## Non-blocking notes

- **N1. Disclosure details.**
  - The real lexicon's hit rates on Linear A and on the control do not depend on the null, so they are already known for all six pairs. Only the null distribution is new. The files imply this ("not blind"); saying it in one line in H-A5-09 would make plain that these runs test the null, not the lexicons.
  - H-A5-09, Part 2 lists Hebrew's Linear A excess but not its H-A5-03 control row (+0.017, p = 0.093). H-A5-12 does not list M2 × Hebrew's control row (+0.006, p = 0.386). Both are in the outcome files of the earlier runs.
  - If H-A5-09 is edited for R1 anyway, these can go in; otherwise the outcome files can list them.
- **N2. Citation rule against the benchmark's bookkeeping.**
  - All six pairs are A under H-A5-03. Under point 4, none of them can be cited as anything but A, whatever this batch shows. The batch is therefore a calibration of the null, which the PR describes honestly as "disclosed checks".
  - For the false-positive benchmark (A5.17), however, "least favourable" in the A < B < C sense is least favourable to the claim. A false positive of an unrelated lexicon under one null would be hidden in the cited label by an A under another.
  - Suggest the A5.17 summary tally false positives per protocol run, not by cited label. Point 4 already keeps each run's own outcome, so no rule change is needed.
- **N3. Power beyond the minimum p** (see check 2). With 38–68% of expanded forms shared with the real lexicon, the outcome files should state that an A under this null is a weak negative. The same held for H-A5-03's null, so this is not new.
- **N4. Research-notes entry.** It records points M1–M3 of the PR #62 re-review accurately. The 266.8 (247–287) figure matches that re-review.

## Assessment
The protocol revision is well motivated, correctly implemented and correctly enforced. The pair files are honest about being re-runs. The defects are in what the immutable protocol text says about its null and about how one descriptive row will be read. They cannot be corrected after merge except by a new entry, so they should be fixed now. A re-review needs to check only R1 and R2.

Verdict: CHANGES REQUESTED
