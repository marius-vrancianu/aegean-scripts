# Independent review — H-A5-03 (Tier 1 protocol, revision 1) with pairs H-A5-03, H-A5-04, H-A5-05, PR #55

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-18) that did not write H-A5-03 to H-A5-05, the stratified null (PR #53), the Turkish lexicon (PR #54) or any part of this PR. Required by `CLAUDE.md` → Merging (review-gated). Given the PR number and the fixed review prompt only.
- **Reviewed:** PR #55 at `f9d4ea9` against `origin/main @ e4e9c69`: `hypotheses/H-A5-03.md`, `H-A5-04.md`, `H-A5-05.md`, the plan change-log line and the research-notes entry; read against Part 1 of `hypotheses/H-A5-01.md`, the outcomes of H-A5-01 and H-A5-02, and the code the files name (`src/aegean/benchmark/{nulls,batch,tier1,lexicons}.py`).
- **Rerun:** the test suite (313 passed, 4 skipped); every lexicon-side figure the files give (below); 1,000 stratified pseudo-lexicons with the protocol seed for English and Turkish (feasibility: 10 s and 6 s); the registration check `batch.check_registered` in a scratch clone where `main` was set to the PR head (H-A5-03 → protocol H-A5-03; H-A5-04 and H-A5-05 → H-A5-03; H-A5-01 and H-A5-02 → H-A5-01).
- **Not done, on purpose:** no hit rate of any real or pseudo-lexicon was computed, on Linear A sign-groups or on the Greek control. No Linear A data and no held-out material were read.
- **Not checkable from the repository:** that no hit rate under the stratified null was seen before registration. It is consistent with what is there: `experiments/A5.17/results/` holds only H-A5-01 and H-A5-02 files and `batch.json`/`batch.md`; no `batch-H-A5-03.*`.

## Summary

The three files are careful and honest: the revision is narrow (one null, one new batch), the non-blindness of the Hebrew and English re-runs is stated prominently, H-A5-04 fixes how each outcome is read, H-A5-05 states its possible biases in advance, and every figure reproduces. The power check is correct. Two things about the batch and the decision rule must be fixed before the merge, because once merged the protocol file is immutable and these are commitments that only the protocol file can make: **the choice between the two protocols is left open for every future pair**, and **a re-run pair has no rule for what happens when its two protocols disagree**. Together they are a forking path (a second null tried on the same question, in a fresh batch) that rule 2 asks to be closed in advance.

## The four required checks

### 1. Null model — sound; one property worth recording (N1)
*Confidence: high (code read; measured lexicon side).*
- `nulls.stratified_matched_lexicon` does what Part 1 says: lengths in increasing order, letters from the real lexicon's positional frequencies at that length, duplicates and overshooting expansions rejected, exact count of distinct expanded forms per length; it refuses a method whose expansion changes lengths. M1's interchanges keep lengths.
- Reproduced exactly in 100 of 100 draws (seed 20261114) for each lexicon: Hebrew 634 / 30 (lengths 3 / 4); English 79 / 310 / 626 (2 / 3 / 4); Turkish 59 / 254 / 546. Totals 664, 1,015, 859 as stated.
- The old matched null's bias, as quoted (100 draws here; the files quote 1,000): Hebrew 622.9 / 41.1 (quoted 623.4 / 40.6), English two-letter 61.3 (quoted 61.7). Consistent.
- The file is right that letter co-occurrence within a form is not matched and that Test 2 remains for that.

### 2. Power check — correct
*Confidence: high.*
- Smallest attainable p is 1/1001 for both tests. Under Benjamini–Hochberg with m = 3 the smallest pair p is adjusted to at most 3 × its raw value, so a raw pair p ≤ 0.0167 reaches adjusted ≤ 0.05 on its own rank; 3/1001 ≈ 0.003 is attainable. The 50-pair ceiling of H-A5-01 is carried over and the code enforces it per protocol (`batch.MAX_PAIRS`).

### 3. Decision rule and batch count — two required changes (R1, R2)
- The decision rule (A / B / C with BH at q = 0.05, raw p deciding A and the first two kinds of B) is H-A5-01's, unchanged. The batch is "every pair ever run under H-A5-03", here 3; the runner keeps one batch per protocol (`batch.records(out_dir, protocol)`), and `admit` refuses a second run of the same pair within a protocol. "Running count of A5 hypotheses registered: 5" is right.
- The problems are about the relation between the two batches; see R1 and R2.

### 4. "What I already know" — complete as far as I can check
- H-A5-03 and H-A5-04 give the full H-A5-01 / H-A5-02 results, the no-two-letter descriptive check, the old null's length bias, and the session's look at individual H-A5-01 matches. H-A5-05 gives the Turkish lexicon-side figures, the link search, and the biases it expects. Each says what was not seen. I found nothing in the repository that the author saw and did not list.
- One lexicon-side fact is not listed because the author did not measure it (N1). It bears on how H-A5-04's outcome B would be read, so it would be worth adding while the files are being revised.

## Required changes

### R1. The protocol must close H-A5-01 to new pairs (or otherwise fix which protocol a pair is run under)
*Confidence: high (code read and simulated).*
- H-A5-03 says: "New pairs should name H-A5-03; the runner still accepts H-A5-01, so that is a convention, not a check." `docs/benchmark.md` and `batch.admit` allow "the same pair … once under each protocol".
- So from this merge on, any new (method, lexicon) pair can be registered and run under both protocols, each in its own batch with its own BH correction, and the more favourable null reported. That is two nulls tried on one question, with no correction across them (rule 2), and it would be legitimate under the files as written.
- The protocol file is the place to fix this, because it becomes immutable at the merge; a later runner check is a plain PR, but it can only enforce what a merged file commits to.
- **Requested:** a sentence in H-A5-03, Part 1, such as: "From the merge of this file, no new pair is registered under H-A5-01. The only pairs run under both protocols are H-A5-01 (Hebrew) and H-A5-02 (English), re-run here as H-A5-03 and H-A5-04." (Wording is the author's choice; what matters is that the set of pairs allowed under both protocols is closed and named.) Enforcing it in the runner can follow as a separate plain PR.

### R2. A pair run under both protocols needs a rule for when the two outcomes differ; H-A5-03, Part 2 (Hebrew) has none
*Confidence: high (read).*
- H-A5-04 fixes in advance how each of its outcomes is read. H-A5-03, Part 2 does not: it says the re-run "adds no new evidence about Hebrew and Linear A", but its decision rule would still label a C as "supported at Tier 1" and qualify the pair for Tier 2, without correction for the earlier test of the same pair under H-A5-01 (outcome A).
- Hebrew is the one pair here that is the substantive claim under test (the Finding 001 / di Mino matcher). A C for it under the second null tried, after an A under the first, is exactly the result a pre-registration should say how to read before it is seen.
- **Requested:** in H-A5-03 (Part 1 or Part 2), a rule for a pair run under both protocols, stated before the runs. Two options I would accept, among others:
  - the pair's Tier 1 outcome is the less favourable of its two outcomes (a C needs C under both protocols), and both are always reported; or
  - for such a pair, the p used for the decision is the larger of its two pair p-values (or the two are BH-corrected together), so the second try is paid for.
  
  And, for Part 2 specifically, the reading of each Hebrew outcome, as H-A5-04 does it (A: as before; B with p1 ≤ α only: …; C: …).

## Non-blocking notes

- **N1. At length 2 the stratified null is close to a copy of the real lexicon.** Under the positional frequencies, the space of distinct two-letter forms after M1's expansion is small: 110 for English, 72 for Turkish. The real lexicons use 79 and 59 of them. In 100 stratified draws (seed 20261114) a pseudo-lexicon shares on average 69.2 of English's 79 and 51.9 of Turkish's 59 two-letter forms. (Hebrew, length 3: 455 of 634 shared, out of 1,100.) Consequences, my reasoning (rule 5), not measured on any input:
  - The two-letter part of the null is nearly fixed, so the tests compare the real lexicon with noise mainly through its three- and four-letter forms. This is intended (it is how the length bias is removed), but it also lowers the null's variance, so a smaller excess at three and four letters can reach significance.
  - For H-A5-04 it means that an outcome B with p1 ≤ α could not come from two-letter forms; it would point to three- and four-letter forms (or co-occurrence), which narrows the reading already given there.
  - Worth adding to "What I already know" of H-A5-04 and H-A5-05 while the files are being revised; the figures here are lexicon side only.
- **N2. `docs/for-marius.md` is not updated.** The item "A revised Tier 1 protocol with a length-stratified matched null …" (line 45) is settled by this PR once merged; CLAUDE.md asks that the PR that settles an item update the inbox. The PR description says "nothing new".
- **N3. No control calibration of the revised null.** H-A5-01 had one before registration (Known-script validation, point 3, with a pass criterion); H-A5-03 deliberately has none, to keep Test 2 blind. I agree with that choice. Suggest that each outcome file report the control line (real against stratified null on the 902 Greek words) explicitly as the null's calibration, deciding nothing.
- **N4. Turkish under the old null** (for the record, lexicon side, 100 draws): two-letter forms 46.6 against the real 59; four-letter 583.7 against 546. Turkish would have had a larger length bias than English under H-A5-01, which supports registering it only under the revised protocol.

## Assessment

The null is implemented and validated as described, the figures reproduce, the power check is right, and the prior-knowledge sections are complete as far as the repository shows. The two required changes concern the batch and decision rule across the two protocols: close H-A5-01 to new pairs (R1), and fix in advance how a pair run under both protocols is decided, including the Hebrew re-run (R2). Both are a few sentences, and both have to be in the files before they become immutable.

Verdict: CHANGES REQUESTED
