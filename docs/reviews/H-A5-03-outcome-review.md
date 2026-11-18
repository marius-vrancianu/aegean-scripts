# Independent review — outcomes of H-A5-03, H-A5-04, H-A5-05 (PR #57)

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-18) that did not write H-A5-03 to H-A5-05, the benchmark code, the outcome files or any other part of this PR. Required by `CLAUDE.md` → Merging (review-gated). It was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #57 at `b3d4cf1` against `main @ 550dc7a`: `hypotheses/outcomes/H-A5-03.md`, `-04.md`, `-05.md`; `experiments/A5.17/results/H-A5-0{3,4,5}-*.{md,json}` and `batch-H-A5-03.{md,json}`; the changes to `docs/benchmark.md`, `docs/for-marius.md`, the plan and `research-notes.md`.
- **Kind of review:** outcomes under `hypotheses/`, reviewed against both lists: the hypothesis items as they bear on the run (did the run follow the frozen files), and the finding items (claims follow from the registered outcome, numbers rerun, circularity, literature).
- **Rerun:**
  - the three registered commands, in the registered order, into a scratch copy of the results directory as it stood on `main @ 550dc7a`. All eight generated files are byte-identical to the committed ones, except for the commit hash in the provenance (`b3d4cf1`, the checkout, instead of `550dc7a`). That is expected. The H-A5-01 batch files and earlier results are untouched by the runs;
  - an independent script (scratch, not committed) that reuses only the input construction, the lexicon loaders, the null generator and `M1.match`/`eligible`/`prepare`, and recomputes hit rates, p1, the control, the length standardisation, Test 2 (with an explicit leave-one-out mean, not the k/(k−1) shortcut) and Benjamini–Hochberg itself. It also checks, over all 1,000 draws of each lexicon, that every pseudo-lexicon has exactly the real lexicon's number of expanded forms at every length. Every figure agrees to the fourth decimal (table below);
  - the test suite: 314 passed, 4 skipped;
  - the guardrail script from `main` against this PR: before this review it fails only for the missing review, as expected.
  - `git diff e4e9c69 550dc7a -- src tests` is exactly PR #56: `batch.check_registered` gains the closed-protocol check, and one test. No computation changed, as the outcome files say. This PR changes nothing under `src/`, `tests/`, `tools/`, `.github/` or `data/`.
- **Not read (blinding respected):** KN Zg 57/58, `data/heldout.txt`, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna. The reruns read Linear A only through `aegean.corpus.load` (training split).

## Summary

The registered results stand. **Outcome A for all three pairs is the label the decision rule gives**, each registered prediction is met, the runs followed the frozen files with no deviation, and every figure I checked reproduces. The cited outcomes under H-A5-03, Part 1, point 4 (Hebrew A, English A) are applied correctly. Confidence: high.

I have no requests that block the merge. There are four notes (N1–N4), all about wording. None changes a p-value, an outcome or a registered reading.

## Checks

### The runs against the frozen hypotheses
- H-A5-03 to H-A5-05 were merged at `550dc7a` (2026-11-18 21:08:22 +0200). The outcome commit is `b3d4cf1` (21:14:10). Each registered command takes about 60 s here, so three runs fit in the interval after the merge. *Confidence: high that the order is right; that each command ran only once rests on the author's statement and cannot be checked from the repository.*
- The code named in the hypotheses (`e4e9c69`) and the code at the run differ only by PR #56, which is registration logic and is disclosed.
- Null: `stratified_matched_lexicon`, K = 1,000, `random.Random(20261114)` in sequence; control the same NeuroDecipher set (902 eligible words); A1.14 harness seed 20261115; α = 0.05. All as registered.
- The stratified null does what Part 1 says: in all 1,000 draws the expanded counts by length equal the real lexicon's (Hebrew 634/30; English 79/310/626; Turkish 59/254/546). Shared two-letter forms with the real lexicon average 69.3 of 79 (English) and 52.0 of 59 (Turkish), as N1 of the PR #55 review reported.
- **Decision rule:** p1 > α and p2 > α for every pair, so A on the raw values, which the batch correction cannot change. BH over (0.871, 0.780, 0.355) gives 0.871 for all three, as reported. Batch count 3, as reported; H-A5-01's batch is unchanged.
- **Predictions:** A for all three; met. Each outcome is read exactly as fixed in advance (Hebrew: "the revised null leaves the Hebrew result unchanged"; English: "the revised null removed English's Test 1 false positive, as intended"; Turkish: A).
- **Cited outcomes (Part 1, point 4):** Hebrew A under both protocols → A. English B (H-A5-02) and A (H-A5-04); the rule "a pair that is A under either is A" gives A. Correctly applied. (H-A5-04's own text, "A or B, as above, leaves it no better than B", read in isolation suggests B; it is overridden by H-A5-03's explicit order A < B < C and "a pair that is A under either is A", and the outcome follows the protocol. Not an issue with this PR.)

### Numbers (independent recomputation)

| Quantity | Outcome files | Independent |
|---|---|---|
| Hebrew: real, false-positive rate, SD | 0.775, 0.773, 0.015 | 0.7754, 0.7727, 0.0153 |
| Hebrew: excess, p1 | +0.003, 0.469 | +0.0026, 0.4685 |
| Hebrew control: excess, p; at Linear A's lengths | +0.017, 0.093; +0.020 | +0.0169, 0.0929; +0.0200 |
| Hebrew: D, p2 | −0.017, 0.871 | −0.0173, 0.8711 |
| English: real, false-positive rate, SD | 0.705, 0.693, 0.020 | 0.7053, 0.6931, 0.0195 |
| English: excess, p1 | +0.012, 0.288 | +0.0122, 0.2877 |
| English control: excess, p; at Linear A's lengths | +0.033, 0.015; +0.028 | +0.0325, 0.0150; +0.0279 |
| English: D, p2 | −0.016, 0.780 | −0.0157, 0.7802 |
| Turkish: real (sign-groups), false-positive rate, SD | 0.657 (272), 0.629, 0.020 | 0.6570 (272), 0.6287, 0.0203 |
| Turkish: excess, pseudo-lexicons ≥ real, p1 | +0.028, 99, 0.100 | +0.0283, 99, 0.0999 |
| Turkish control: excess, p; at Linear A's lengths | +0.032, 0.017; +0.022 | +0.0320, 0.0170; +0.0218 |
| Turkish: D, p2 | +0.006, 0.355 | +0.0064, 0.3546 |
| Turkish, SigLA alone (descriptive): p | 0.042 | 0.0420 |
| BH-adjusted pair p (all three) | 0.871 | 0.8711 |

Arithmetic in the prose also checks: 0.0283 × 414 ≈ 12 sign-groups; the H-A5-01 and H-A5-02 comparison figures (0.769, +0.006, SD 0.017; 0.641, +0.065, SD 0.029; two-sign row 0.796 / 0.718; 84% of draws with p1 ≤ α) match the earlier results files. The per-source, by-length, stability, Finding 001 null, size-curve, random-string and degrees-of-freedom figures in the three outcome files match the generated reports.

### Claims follow from the registered outcome or are labelled
- Outcome labels, p-values, "as predicted" and the cited outcomes follow from the registered rules.
- Turkish's near miss is reported plainly, with the per-source and resampling figures marked descriptive and the pre-registered reading of a Test 1-only B quoted. That is the right handling.
- "Hebrew does worse against noise than English or Turkish" is a descriptive ranking of point estimates, not a test; it is not presented as more. Acceptable.
- The control-row observation (unrelated lexicons ahead of length-matched noise on Greek words) is labelled descriptive in the PR description and its mechanism is labelled the author's reasoning. See N2 for the wording in the outcome file and `docs/benchmark.md`.

### Circularity
- Lexicons: Strong's Hebrew via openscriptures; English from WordNet/CMUdict; Turkish from Zemberek-NLP ranked by FrequencyWords. None is derived from an Aegean source. Linear A is read in conventional Linear B values (L1, stated); the control is the NeuroDecipher Linear B–Greek data. The null is built only from each real lexicon's own positional letter frequencies. No value or reading here was derived from a lexicon under test. *Confidence: high.*
- The Hebrew and English pairs are non-blind re-runs, disclosed in the hypotheses and outcomes; they test the null, not Hebrew or English against Linear A, and the outcomes say so.

### Literature
- The outcomes make no claim about the language of Linear A and say so. Their methodological lesson, that a chance baseline for lexical matching must match the lexicon's form lengths and phonotactics, and that matching positional frequencies alone leaves residual structure, agrees with the literature on chance resemblance in language comparison: Ringe 1992 (*On Calculating the Factor of Chance in Language Comparison*) and Kessler 2001 (*The Significance of Word Lists*), whose permutation tests keep real words intact rather than generating forms, so that within-word phonotactics are preserved by construction. The "Next candidates" line (a bigram-matched null) is in the same direction. I cite these from memory, not at first hand. *Confidence: medium-high; not a blocker.*

## Notes (non-blocking)

**N1. `docs/benchmark.md`, Limits: the edited bullet contradicts itself.** It now opens "H-A5-01's matched null under-draws short forms (fixed by the length-stratified null of H-A5-03)" but still ends "A length-stratified null is a candidate for a revised protocol." The last sentence is stale and should go. *Confidence: high.*

**N2. The control-row observation is worded more generally than the data allow.** The outcome of H-A5-04 heads it "The finding this pair adds", and `docs/benchmark.md` says in bold "Real lexicons beat length-matched noise on Greek words". What was measured: two of three lexicons (English p = 0.015, Turkish p = 0.017; Hebrew +0.017, p = 0.093), uncorrected, on a row the protocol registers as descriptive. Suggested wording: "a descriptive observation" in the heading, and "two of the three lexicons" in the text. Also, for English an alternative contributor is not mentioned: English is Indo-European like Greek, which H-A5-02 named as a pull on the control. Turkish's equal advantage (+0.032) argues that relatedness is not the main cause, but the outcome could say that rather than leave the letter co-occurrence reading as the only one. `research-notes.md` is append-only, so any change there belongs in a later entry. *Confidence: high on the counts; the IE point is a reading, not a measurement.*

**N3. "The size of the drop is close to what the descriptive check of H-A5-02 suggested (without two-letter forms, −0.007)"** (outcome of H-A5-04). The result, +0.012, lies between +0.065 and −0.007, which is what H-A5-04 expected in advance ("a result between the two ... well below +0.065"). "Between the two, nearer the check without two-letter forms, as expected" would be exact; "close to −0.007" overstates the agreement slightly. *Confidence: high.*

**N4. Test 2's difference D is negative for Hebrew and English in nearly all resampling draws** (combined intervals −0.032 to +0.002 and −0.036 to −0.003). That is, both lexicons' advantage over noise is larger on Greek words than on Linear A. This does not affect any decision (Test 2 is one-sided), and the outcome files report the intervals. I note it because Test 2 assumes the non-linguistic advantage is equal on both inputs; a consistently negative D is weak evidence that it is not, in the direction that makes Test 2 conservative for these lexicons. Worth one sentence when Test 2's equal-shift assumption is next discussed (the outcome of H-A5-05 already lists it under "Not shown"). *Confidence: medium; descriptive.*

## Process
- First line of the PR description: "**Review-gated: `docs/reviews/H-A5-03-outcome-review.md`**", which is this file.
- No rule file, held-out file or enforcement code is touched. `research-notes.md` and the plan change only by appended lines; the `docs/for-marius.md` changes move the runner item (done in PR #56) out of the to-do list and add an information-only item.
- Before this review, CI (`test`) failed for the missing review, as expected for a review-gated PR.

Verdict: APPROVE
