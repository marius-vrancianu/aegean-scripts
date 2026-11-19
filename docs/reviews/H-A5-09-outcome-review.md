# Independent review: outcomes of H-A5-09 to H-A5-14 (protocol H-A5-09, position-aware bigram null), PR #65

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-19). I did not write H-A5-09 to H-A5-14, the position-aware null, the outcome files or any other part of this PR. `CLAUDE.md` → Merging (review-gated) requires this review. I was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #65 at `da83d1d` against `main @ fbde909`. Files: `hypotheses/outcomes/H-A5-09.md` to `-14.md`; `experiments/A5.17/results/H-A5-09`–`14-*.{md,json}` and `batch-H-A5-09.{md,json}`; the change to `experiments/A5.17/null_validation.py` and `results/null-validation.json`; the changes to `docs/benchmark.md`, `docs/for-marius.md`, the plan and `research-notes.md`. I read them against `hypotheses/H-A5-09.md` (Part 1) and `H-A5-10.md` to `-14.md`, the review of PR #63 (`docs/reviews/H-A5-09-review.md`, including both re-reviews) and `src/aegean/benchmark/{nulls,tier1,batch,m1,m2}.py`.
- **Kind of review:** outcomes under `hypotheses/`, so I used both lists. From the hypothesis list, as it bears on the run: did the run follow the frozen files? From the finding list: do the claims follow from the registered outcomes, do the numbers rerun, is there circularity, and what does the literature say?
- **Rerun:**
  - **The six registered commands**, in the registered order, into a scratch copy of `experiments/A5.17/results/` as it stands on `main @ fbde909`. All 14 generated files are byte-identical to the committed ones. The one exception is the provenance commit hash: my checkout is `da83d1d`, the run's was `fbde909`, which is expected. `batch-H-A5-09.{md,json}` are identical byte for byte.
  - **An independent script** (scratch, not committed). It reuses only the corpus loading (training split), the primary reading, input construction, the lexicon loaders and the methods' `expand`/`eligible`/`hits`; neither matcher has changed since earlier reviews checked them (M2 by brute force in the review of PR #62). It reimplements the rest:
    - the position-aware bigram generator, written from the text of H-A5-09, Part 1;
    - hit rates, Test 1, the length standardisation of the control, Test 2 with an explicit leave-one-out mean, and Benjamini–Hochberg, all in exact `Fraction` arithmetic.

    My generator draws the same 1,000 pseudo-lexicons per pair from `random.Random(20261114)`. Over all 6,000 of them I found no violation of two properties: the expanded-form count by length equals the real lexicon's, and every first letter and every transition was seen in the real lexicon at the same length and position. Every figure agrees with the committed JSON (table below).
  - **`null_validation.py`:** run under `PYTHONHASHSEED=1` and `=987`. The two outputs are identical to each other and to the committed `null-validation.json`. The three changed values in that file differ only in the 17th significant digit.
  - **The test suite:** 336 passed, 4 skipped.
  - **The guardrail script from `main`**, with the PR body: before this review it fails only because the review is missing, as expected.
- **Code between the registered commit and the run:** `git diff 7b96bbe fbde909 -- src tests tools` and `git diff fbde909 da83d1d -- src tests tools .github data` are both empty. The outcome files say `src/` did not change, and that is correct.
- **Not read (blinding respected):** KN Zg 57/58, `data/heldout.txt`, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna. I read Linear A only through `aegean.corpus.load` (training split).

## Summary
**The registered results stand.** For all six pairs, outcome A is the label the decision rule gives. Every prediction is met. The runs followed the frozen files with no deviation that I can find. Every number in the decision reproduces exactly, and so do the batch and the calibration reading. Confidence: high.

**One request blocks the merge (R1), and it concerns wording only.** "Nearest any pair has come to passing Test 1 under any protocol" (H-A5-11) is false: M1 × English *passed* Test 1 under H-A5-01 (H-A5-02, p1 = 0.009). The same claim, in the form "closest yet", appears in the new research-notes heading and in Marius's inbox. The research-notes entry becomes append-only once merged. No p-value, outcome or registered reading is affected.

## Checks

### The runs against the frozen hypotheses
- **Timing.** PR #63 was merged at `fbde909` (09:07:08 +0200). The outcome commit `da83d1d` is at 09:16:57. Six runs of about 60 s each fit in that interval. *Confidence: high that the runs followed the merge. That each command ran only once rests on the author's statement and cannot be checked from the repository.*
- **Null and seeds:** `positional_bigram_matched_lexicon` (`batch.PROTOCOLS["H-A5-09"]["null"] == "posbigram"`), K = 1,000, `random.Random(20261114)` in sequence, as registered. The A1.14 seed is 20261115 and α = 0.05. The methods run at their default rules. The control is the NeuroDecipher set: 902 eligible words under M1 and 881 under M2, as in the power checks.
- **Commands:** each outcome quotes its hypothesis file's command exactly (`--protocol H-A5-09` to `H-A5-14`). The runner resolves H-A5-10 to H-A5-14 to protocol H-A5-09 through their `**Protocol:**` lines.
- **The decision rule.** p1 > α and p2 > α for every pair, so every pair is A on the raw values. The batch correction cannot change an A.
  - BH over the six pair p-values (0.9311, 0.3387, 0.5824, 0.8961, 0.5984, 0.6823) gives 0.9311 for all six, as reported.
  - The batch count is 6, within the limit of 50.
- **Margin on M1 × Turkish:** p1 = 52/1001. Of the 1,000 pseudo-lexicons, 51 match at least as often as the real lexicon, and 49 or fewer would have been needed for p1 ≤ α. So Test 1 missed by two pseudo-lexicons. Test 2 (p2 = 0.582) and the batch threshold for C (raw pair p ≤ 0.0083) were far out of reach, so the outcome would have been B at most.
- **Point 4 (cited outcome = least favourable of all runs).** Every pair is cited as A. For English (B, A, A) the least favourable in the order A < B < C is A. That is correct.
- **Point 5 (false positives per protocol run).** No pair has raw p2 ≤ α, so this protocol has no false positive. `docs/benchmark.md` now lists each protocol's runs separately, as point 5 requires.
- **Reported besides the decision.** Each outcome file gives the control row beside the H-A5-03 row, as Part 1 requires.

### The calibration reading fixed in advance
- **The figures.** Raw control excess against this null: English +0.01044 (p 0.162), Turkish +0.02531 (p 0.012). The registered comparison is with the raw H-A5-03 rows (+0.033, +0.032), so the raw rows are the right ones to use.
- **The branches.**
  - Branch 1 needs both excesses below +0.010; English is not below it.
  - Branch 2 needs both at or above +0.020 with p ≤ 0.05; English is neither.
  - So the reading is the third branch, **inconclusive**, and that label is correct.
- **The label is robust to English's boundary.** English sits only 0.0004 above +0.010, which is less than one control word's worth of hits (1/902 ≈ 0.0011). Its length-standardised excess is +0.008. But the reading would be inconclusive either way: Turkish's second-branch values rule out branch 1, and English's p rules out branch 2.
- **The reason given is wrong, though; see N1.**

### Numbers (independent recomputation)

| Pair | Linear A real, FPR, excess, p1 | Control real, FPR, excess, p; at Linear A's lengths | D, p2 | Mean overlap |
|---|---|---|---|---|
| H-A5-09 M1 × Hebrew | 0.7754, 0.7838, −0.0084, 0.7812 | 0.5322, 0.5224, +0.0098, 0.1668; +0.0134 | −0.0219, 0.9311 | 0.794 |
| H-A5-10 M1 × English | 0.7053, 0.6929, +0.0124, 0.1369 | 0.4900, 0.4796, +0.0104, 0.1618; +0.0078 | +0.0046, 0.3387 | 0.582 |
| H-A5-11 M1 × Turkish | 0.6570, 0.6355, +0.0215, 0.0519 | 0.4124, 0.3871, +0.0253, 0.0120; +0.0237 | −0.0022, 0.5824 | 0.638 |
| H-A5-12 M2 × Hebrew | 0.3201, 0.3411, −0.0210, 0.8961 | 0.3530, 0.3641, −0.0110, 0.7892; −0.0153 | −0.0057, 0.6214 | 0.749 |
| H-A5-13 M2 × English | 0.7354, 0.7365, −0.0010, 0.5984 | 0.7242, 0.7224, +0.0018, 0.4665; −0.0015 | +0.0004, 0.4985 | 0.531 |
| H-A5-14 M2 × Turkish | 0.7169, 0.7225, −0.0055, 0.6823 | 0.6243, 0.6264, −0.0021, 0.5714; −0.0068 | +0.0013, 0.4705 | 0.586 |

- **Agreement:** every value equals the committed JSON to every printed digit. The overlap range, 0.53 to 0.79, matches H-A5-09, Part 1.
- **Other figures:** the per-source rows, the null standard deviations (including the H-A5-03 values they are compared with), the earlier-run figures quoted under "Blind" and "Earlier runs", and the shares of resampling draws all match the generated reports.
- **Two stability bounds are mis-transcribed** (N2).

### Claims follow from the registered outcome or are labelled
- **Follow from the registered rules:** the outcome labels, the p-values, "as predicted", the batch, the cited outcomes, "no false positive of this protocol" and "inconclusive".
- **Limits:** "Weaker negative" is carried into every outcome file, with the length-2 identity, as H-A5-09, Part 1 and review N3 of PR #63 asked.
- **Descriptive readings:** the comparison with the +0.023 / +0.022 estimate is labelled descriptive ("my reading, rule 5").
- **Unlabelled interpretive sentences:** H-A5-11's "how close this came" section has a few. They are mild, but one is false (R1) and two overstate what was measured (N3).
- **`docs/benchmark.md`:** the new false-positive line is accurate ("fired once … came close once more").
- **The research-notes summary** "two lexical-matching methods, with three nulls of increasing strictness, never tell a real lexicon from noise on Linear A more than on Greek words" is a fair summary of 14 Test 2 results with no p2 ≤ α.

### Circularity
- **Lexicons, classes, readings and control:** unchanged from PR #62 and checked there. The lexicons are Strong's Hebrew, WordNet/CMUdict English and Zemberek/FrequencyWords Turkish. The classes are LingPy's DOLGO table. Linear A is read in conventional Linear B values (L1). The control is NeuroDecipher's Linear B–Greek data.
- **The null:** fitted only to each real lexicon's own forms, by length and position. It is not fitted to any Aegean input.
- **The calibration thresholds:** fixed in H-A5-09 before any pseudo-lexicon hit rate under a bigram null had been seen (its "Not seen" line), and I have no evidence otherwise.

No value or reading here was derived from a lexicon under test. *Confidence: high.*

### Literature
- **No claim about Linear A's language.** The outcomes make none: they are rows of a false-positive benchmark. The result agrees with the long-standing finding that chance resemblances between unrelated word lists are frequent, and that only a permutation or surrogate baseline gives them a meaning: Ringe 1992, "On calculating the factor of chance in language comparison"; Baxter & Manaster Ramer 2000; Kessler 2001, *The Significance of Word Lists*.
- **Markov-chain pseudo-words.** These are the standard way to make pseudo-words that keep a lexicon's local phonotactics. Psycholinguistic generators such as Wuggy (Keuleers & Brysbaert 2010, *Behavior Research Methods* 42) filter real words out of their output. This null does not, and at length 2 it cannot. That is the copying problem the outcome files call a "weaker negative", and the literature supports the caveat.
- **A null that keeps more of the data's structure is more conservative against the data.** This is the usual trade-off in surrogate-data testing (Theiler et al. 1992, *Physica D* 58). It fits the narrower null spread reported here.
- I cite these from memory, not at first hand. *Confidence: medium-high; not a blocker.*

## Required change

**R1. "Nearest any pair has come to passing Test 1" / "closest yet on Test 1" is false.**

*Where:*
1. `hypotheses/outcomes/H-A5-11.md`, "How close this came": "This is the nearest any pair has come to passing Test 1 under any protocol";
2. `research-notes.md`, the heading of the new entry: "Turkish closest yet on Test 1" (the entry is new in this PR, so it can still be edited now, but not after the merge);
3. `docs/for-marius.md`: "M1 × Turkish came closest yet on the first test (p = 0.052)".

*Why it is false:* M1 × English passed Test 1 under H-A5-01 (H-A5-02 outcome B, p1 = 0.009, an outcome in this same benchmark). `docs/benchmark.md` in this PR states it correctly: Test 1 "fired once (English, H-A5-01's null) and came close once more (Turkish under H-A5-09)".

*Suggested wording* (any equivalent is fine):
- **H-A5-11:** "This is the nearest any pair has come to passing Test 1 without passing it (English passed under H-A5-01, H-A5-02: p1 = 0.009)".
- **Research-notes heading:** "Turkish nearly passes Test 1".
- **Inbox:** "M1 × Turkish nearly passed the first test (p = 0.052; only English under the first null did pass it)".

*Why blocking:* the research-notes entry becomes append-only on merge, and the inbox line is what Marius reads. Both would record a false statement about the benchmark's own history. *Confidence: high.*

## Notes (non-blocking; none affects an outcome, a p-value or the registered reading)

- **N1. The reason given for "inconclusive" is wrong** (H-A5-10 and H-A5-11, calibration section).
  - The text says English is "just above the +0.010 boundary of the first branch", Turkish is in the second branch, and "one lexicon each way is the third branch". But English is not in the first branch. It lies between +0.010 and +0.020, which is the third branch on its own terms.
  - Suggested: "English's excess (+0.0104) lies between +0.010 and +0.020, just above the first branch's boundary; Turkish meets the second branch's conditions. Either fact makes the reading inconclusive."
  - Best fixed together with R1, since the files are being edited anyway.
- **N2. Two stability bounds are mis-transcribed** from the generated reports.
  - H-A5-09: "excess −0.018 to +0.010"; the report has −0.018 to +0.009 (high 0.00946).
  - H-A5-11: "+0.013 to +0.037"; the report has +0.012 to +0.037 (low 0.01249).
- **N3. Two sentences in H-A5-11 overstate what was measured.**
  - "Test 1 alone would have called it at about even odds over resampling": 42% of draws is less than even. Say "in about two draws out of five".
  - "Turkish differs from even this structure-matched noise in some way that helps on any input": two inputs were measured, not any. Say "that helps on both Linear A and the Greek words", and label it descriptive.
- **N4. "This null is narrower than H-A5-03's because it shares more forms with the real lexicon"** (all six files) is stated as fact.
  - The mechanism is sound: forms that every pseudo-lexicon shares with the real lexicon add hits common to all of them and no variance between them.
  - But it was not separated from the bigram constraint itself, which also narrows the space of pseudo-lexicons. "Mainly because", or labelling it as the likely reason, would be exact.
- **N5. The +0.023 / +0.022 estimate** was given at *low* confidence in re-review 1 of PR #63, and its assumption is inexact. The calibration paragraph compares the observed figures with it ("English's drop is larger than that estimate; Turkish's is close to it"). Adding "(low-confidence estimate)" would keep the comparison from reading as a test.
- **N6. The adjusted p in the per-pair reports.** Each generated `.md`/`.json` records the batch-adjusted p as it stood when that pair was run: batch of 1, 2 and so on, so H-A5-10's report shows 0.6773. The outcome files correctly quote the final batch (0.931). This is the runner's existing behaviour (the H-A5-03 batch shows the same), but a reader of a single report could be misled. A later plain PR could have `python -m aegean.benchmark.batch` note in each report that the batch file is authoritative.
- **N7. "Control under H-A5-03: H-A5-03: +0.017"** (H-A5-09 outcome) repeats the label. This is cosmetic.

## Process
- **Description:** its first line is "**Review-gated: `docs/reviews/H-A5-09-outcome-review.md`**", which is this file.
- **Files touched:** no rule file, held-out file or enforcement code. Under `experiments/`, only an exploration script (`null_validation.py`) changes, and its output is reproducible bit for bit. `research-notes.md` and the plan change only by appended lines against `main`.
- **Inbox:** `docs/for-marius.md` gains an information-only item, which R1 asks to reword.
- **CI:** before this review, CI (`test`) failed for the missing review, as expected. With this verdict it will keep failing until a re-review approves.
- **After R1:** once the author has fixed R1, a reviewer (this instance or a new one) appends a re-review to this file.

Verdict: CHANGES REQUESTED

---

# Re-review 1 (PR #65 at `dcc1d0a`)

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-19). I did not write this PR, the fix commit or the first review above. I was given the PR number and the fixed review prompt only.
- **Reviewed:** the fix commit `dcc1d0a` (R1, N1–N5, N7), the correction it adds to the merged `hypotheses/outcomes/H-A5-05.md`, and, again, every figure in the six outcome tables against the generated reports.
- **Rerun:**
  - The six registered commands, in order, into a scratch copy of `experiments/A5.17/results/` from `main @ fbde909`. All 14 generated files are identical to the committed ones except the provenance commit hash (`dcc1d0a` against `fbde909`, one line per file). `batch-H-A5-09.{md,json}` is identical byte for byte.
  - `git diff da83d1d dcc1d0a -- src tests tools .github data experiments` is empty, so the fix touched no code and no generated output.
  - Test suite: 336 passed, 4 skipped. Guardrail script from `main` with the PR body: it fails only on the missing APPROVE, as expected. `research-notes.md` against `main` has no removed or changed line. Editing `hypotheses/outcomes/H-A5-05.md` is allowed (`MUTABLE` in the script).
- **Not read (blinding respected):** KN Zg 57/58, `data/heldout.txt`, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna.

## Summary
**R1 is fixed in all three places, and N1–N5 and N7 are taken up correctly.** The outcomes, p-values, batch and calibration label still stand (confidence: high).

**Two new requests block the merge.**
- **R2:** eight figures in the outcome files are mis-copied in the third decimal from the generated reports. The first review did not check these columns.
- **R3:** the R1 fix goes further than R1. In the merged H-A5-05 outcome and in the new research-notes entry, it records as false two statements that were true, or only ambiguous, in their context. The research-notes entry becomes append-only on merge.

Neither request changes an outcome, a decision p-value or the calibration reading.

## R1 and the notes: checked
- **R1.**
  - H-A5-11 now reads "the nearest an outcome-A pair has come to passing Test 1", with English's p1 = 0.009 (H-A5-02, outcome B) in brackets.
  - The research-notes heading and the inbox line are reworded to match.
  - The fact claimed is true. Outcome-A runs had p1 of 0.397, 0.469, 0.288, 0.100, 0.946, 0.716 and 0.671 before this protocol, and 0.052 is the lowest (`docs/benchmark.md`, "Results so far").
  - One wording point is folded into R3: "outcome-A *pair*" should be "outcome-A *run*".
- **N1.** The calibration paragraph now places English (+0.0104) in the middle band and says that Turkish alone also rules out branch 1. That is correct against H-A5-09, Part 1.
- **N2.** The stability bounds are now −0.018 to +0.009 (H-A5-09) and +0.012 to +0.037 (H-A5-11). They match the reports (line 54, "both" column).
- **N3, N4, N5, N7.** Each is taken up as suggested. The N4 wording ("my reading, not tested") is exact.

## Required changes

**R2. Eight figures in the outcome files differ from the generated reports.** The source is each pair's `experiments/A5.17/results/H-A5-NN-*.md` (primary row at line 20; Test 2 at line 13), and its JSON agrees with it.

| File | Where | Outcome file | Report / JSON |
|---|---|---|---|
| H-A5-09 | Test 1 row, 95% band, low end | 0.759 | **0.758** (0.75845) |
| H-A5-10 | Test 1 row, 95% band, low end | 0.672 | **0.671** (0.67150) |
| H-A5-11 | Test 1 row, false-positive rate | 0.636 | **0.635** (0.63546) |
| H-A5-11 | Test 2 row, 95% band, high end | +0.024 | **+0.023** (0.02345) |
| H-A5-11 | "Per source", lineara.xyz excess | +0.024 | **+0.023** (0.02348) |
| H-A5-13 | Test 1 row, false-positive rate | 0.737 | **0.736** (0.73648) |
| H-A5-13 | "Greek control at Linear A's lengths" | −0.002 | **−0.001** (−0.00146) |
| H-A5-14 | Test 1 row, false-positive rate | 0.723 | **0.722** (0.72248) |

- **Fix:** copy these eight values from the reports. I compared every other number in the six tables, the per-source lines and the stability lines with the JSON at three decimals, and they agree.
- **Why blocking:** an outcome file is the record that later work cites. It should not disagree with the output it reports, and the fix is mechanical.
- **What it does not affect:** no decision quantity. p1, p2, D, the pair p, the batch and the calibration figures are all correct.
- **About the first review:** its table compared the JSON with its own recomputation, and both are right. The 3-decimal transcriptions in the outcome files were not checked column by column.
- *Confidence: high.*

**R3. The H-A5-05 correction and the new research-notes entry overstate what was wrong.**
- **H-A5-05's sentence:** "This is the nearest any pair has come to passing". It does not say "Test 1". When it was written there were five runs (H-A5-01 to H-A5-05), and their pair p were 0.840, 0.754, 0.871, 0.780 and 0.355. The pair p decides the outcome, and their p2 were the same values.
  - On Test 2 and on the pair p, Turkish (0.355) *was* the nearest any pair had come to passing.
  - Only if "passing" means Test 1 is the sentence false.
  - So the sentence was ambiguous, not "wrong as written", which is what the added correction says.
- **The 2026-11-18 research-notes entry:** its "Turkish came closest" sits under a table of the three H-A5-03 runs, and among those three it is true. The new entry (`research-notes.md`, "PR #65, first review") says that entry carries "the same claim", and it does not.
- **Why blocking:** the new research-notes entry becomes append-only on merge. It would permanently record that two earlier statements were false when they were not. This is the reason R1 was blocking.
- **Suggested wording** (any equivalent is fine):
  - **H-A5-05 correction:** "*Correction (2026-11-19, review of PR #65):* 'nearest any pair has come to passing' is ambiguous. It is true of Test 2 and of the pair p (0.355, the lowest of the five runs then made). It is false of Test 1: M1 × English passed Test 1 under H-A5-01's null (p1 = 0.009; outcome B, H-A5-02). This p1 (0.100) was the lowest of the outcome-A runs at that point. No figure or outcome changes."
    - Also move the block quote after the bullet list, or before "This is the nearest…". At present it splits the line that ends in ":" from its list.
  - **New research-notes entry:** replace the sentence about the H-A5-05 outcome and the 2026-11-18 entry with: "The merged H-A5-05 outcome said Turkish was 'the nearest any pair has come to passing'. That is true of Test 2 and the pair p but not of Test 1, so it gets a dated clarifying note. The 2026-11-18 entry's 'Turkish came closest' refers to the three H-A5-03 runs and is correct as written."
  - **"pair" → "run":** English's *cited* outcome is also A (`docs/benchmark.md`: "English A"), so "the nearest outcome-A pair" could include English, which passed Test 1. "Run" is exact.
    - Required in the research-notes heading ("Turkish the nearest A run to Test 1") and in the body bullet ("the nearest an outcome-A run has come").
    - Recommended, not required, in H-A5-11 and the inbox line. There the brackets already remove the ambiguity, and the files stay editable.
- *Confidence: high on the facts (pair p and p2 from `docs/benchmark.md` and the outcome files). Medium on what the H-A5-05 author meant by "passing". That uncertainty is the point: the record should not settle it as "wrong".*

## Notes (non-blocking)
- **N8. The PR description** does not mention the edit to the merged `hypotheses/outcomes/H-A5-05.md`. A merged outcome being changed is something Marius would want to see in the description. Add one bullet under "What this does".
- **N9. "Nearest to passing" will need a new qualifier.** Under this protocol, H-A5-10 (M1 × English) has the lowest pair p of any run so far (0.339, against Turkish H-A5-05's 0.355). No file in this PR claims otherwise. Any later summary of "closest to passing" should name the test it means.
- N6 from the first review is still open and is fine as a later plain PR.

## Process
- The first line of the description still names this file. The fix commit is on the PR branch and does not touch code.
- After R2 and R3 are fixed, a reviewer appends re-review 2 to this file.

Verdict: CHANGES REQUESTED

---

# Re-review 2 (PR #65 at `e310dad`)

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-19). I did not write this PR, either fix commit, the first review or re-review 1. I was given the PR number and the fixed review prompt only.
- **Reviewed:** the fix commit `e310dad` (R2, R3, N8); again every figure in the six outcome tables, per-source lines, stability lines and null-spread lines against the generated JSON; the edit to the merged `hypotheses/outcomes/H-A5-05.md`; the two new research-notes entries, the inbox line and the PR description.
- **Rerun:**
  - The six registered commands, in order, into a scratch copy of `experiments/A5.17/results/` from `main @ fbde909`. All 12 per-pair files differ from the committed ones only in the provenance commit hash (`e310dad` against `fbde909`, one line per file). `batch-H-A5-09.{md,json}` is identical byte for byte.
  - `git diff dcc1d0a e310dad -- src tests tools .github data experiments` is empty: the fix touched no code and no generated output.
  - `null_validation.py` under `PYTHONHASHSEED=42` (a third seed, after the first review's 1 and 987): output identical to the committed `null-validation.json`.
  - Test suite: 336 passed, 4 skipped.
  - Guardrail script from `main`, with the current PR body: it fails only because the review file's last verdict is CHANGES REQUESTED, as expected before this re-review.
  - `research-notes.md` and the plan against `main`: no removed or changed line.
- **Not read (blinding respected):** KN Zg 57/58, `data/heldout.txt`, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna. Linear A only through the registered runner (training split).

## Summary
**R2, R3 and N8 are fixed. Nothing blocks the merge.** The six outcomes (all A), the decision p-values, the batch (adjusted 0.931 for all six) and the calibration label (inconclusive) stand. Confidence: high.

## Checked

**R2 (eight figures).** All eight now match the reports: H-A5-09 band low 0.758; H-A5-10 band low 0.671; H-A5-11 false-positive rate 0.635, Test 2 band high +0.023, lineara.xyz +0.023; H-A5-13 false-positive rate 0.736, control at Linear A's lengths −0.001; H-A5-14 false-positive rate 0.722. I then compared, by script, every other figure in the six tables with the JSON at three decimals: real rate, false-positive rate and 95% band for Test 1; the control row; the control at Linear A's lengths; D, its band and p2; the pair p; the three per-source excesses and p; the stability interval and both shares of draws; the null sd. All agree. The earlier-run figures quoted in the files (H-A5-03 to -08 control excess and p, null sd) also agree with those runs' JSON.
- The new research-notes bullet attributes the errors to "hand-rounding of four-decimal values". That fits all eight: each wrong value is what rounding the four-decimal value gives (for example 0.75845 → 0.7585 → 0.759), and each correct value is the direct three-decimal rounding.

**R3 (H-A5-05 note and research-notes entry).**
- The H-A5-05 note now says the sentence is ambiguous: true of Test 2 and of the pair p, false of Test 1. The facts check: the pair p of the five runs then made were 0.840, 0.754, 0.871, 0.780 and 0.355, and p2 had the same values (`docs/benchmark.md`; H-A5-02 to -05 JSON). The p1 of the outcome-A runs were 0.397, 0.469, 0.288 and 0.100. English passed Test 1 under H-A5-01 (p1 = 0.009, outcome B).
- The note now sits after the bullet list, so the line ending in ":" leads into its list again.
- The research-notes entry "PR #65, first review" now says the 2026-11-18 "Turkish came closest" refers to the three H-A5-03 runs and is correct as written. That is so: it sits under the H-A5-03 to H-A5-05 table (line 947).
- "pair" → "run" is made in the research-notes heading and body bullet (required), and in H-A5-11 and the inbox line (recommended).
- Editing a merged outcome file is allowed (`MUTABLE` in the guardrail script) and is review-gated; this review covers it.

**N8.** The PR description now has a bullet for the edit to the merged H-A5-05 outcome, and one for the R2 figures.

## Notes (non-blocking)
- **N10.** The H-A5-05 block is headed "Correction", while the commit title and the research-notes entry call it a "clarifying note". Re-review 1 suggested "Correction" itself, and the note's text is exact, so this is cosmetic. The outcome file stays editable; "Clarification" would match the research notes.
- **N11.** The inbox line says Turkish "came closest of the runs that came out A", and the bracket ties that to the first test. On the pair p, H-A5-10 (M1 × English, 0.339) is now the lowest of any run (re-review 1, N9). The bracket makes it clear enough. "Came closest on the first test" would be exact, and the inbox can be edited later.
- **N6** (per-pair reports show the batch-adjusted p as it stood when each pair ran) remains a candidate for a later plain PR.

## Process
- The first line of the description still names this file. No rule file, held-out file or enforcement code is touched.
- This re-review is committed to the PR branch; with it, the last verdict in this file is APPROVE.

Verdict: APPROVE
