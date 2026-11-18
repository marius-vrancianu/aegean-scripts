# Independent review — outcomes of H-A5-06, H-A5-07, H-A5-08 (M2 × Hebrew, English, Turkish), PR #62

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-18). I did not write H-A5-06 to H-A5-08, M2, the outcome files or any other part of this PR. Required by `CLAUDE.md` → Merging (review-gated). I was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #62 at `4e2340d` against `main @ 4280cf1`: `hypotheses/outcomes/H-A5-06.md`, `-07.md`, `-08.md`; `experiments/A5.17/results/H-A5-0{6,7,8}-M2-*.{md,json}`, `batch-H-A5-03.{md,json}`, `M2-class-reweighted-test2.json`; `experiments/A5.17/m2_threshold_calibration.py`, `m2_class_reweighted_test2.py`; the changes to `docs/benchmark.md`, `docs/for-marius.md`, the plan and `research-notes.md`. Read against `hypotheses/H-A5-01.md` (Part 1), `H-A5-03.md` (Part 1), `H-A5-06.md` to `-08.md`, the review of PR #60 (`docs/reviews/H-A5-06-review.md`) and `src/aegean/benchmark/{m2,tier1,nulls,batch}.py`.
- **Kind of review:** outcomes under `hypotheses/`. I used both lists. From the hypothesis list, as it bears on the run: did the run follow the frozen files? From the finding list: do the claims follow, do the numbers rerun, is there circularity, what does the literature say?
- **Rerun:**
  - **The three registered commands**, in the registered order, into a scratch copy of `experiments/A5.17/results/` as it stands on `main @ 4280cf1`. All eight generated files are byte-identical to the committed ones, except for the commit hash in the provenance (`4e2340d`, the checkout, instead of `4280cf1`), which is expected. Each run took about 60 s.
  - **An independent script** (scratch, not committed). It reuses only the corpus loading and primary reading, the input construction, the lexicon loaders, the stratified null generator, and `M2.skeleton`/`M2.eligible` (sign to class string). It reimplements the rest:
    - Levenshtein and the 1/4 rule, in exact integer form (4·d ≤ max length);
    - the reach sets, Test 1, the control standardisation, Test 2 with an explicit leave-one-out mean, and Benjamini–Hochberg.

    It also checks the matcher by brute force against every form, and against `M2.hits`, for the real lexicon and 10 pseudo-lexicons of each language. Over all 1,000 draws it checks that every pseudo-lexicon has the real lexicon's number of forms at every length. Every figure agrees to the fourth decimal (table below).
  - **`m2_class_reweighted_test2.py`:** its output is byte-identical to the committed JSON.
  - **`m2_threshold_calibration.py`:** it reproduces the quoted 1/4 figures; see N3 for the 1/3 figures.
  - **The test suite:** 335 passed, 4 skipped.
  - **The guardrail script from `main`**, with the PR body: before this review it fails only for the missing review, as expected.
- **Code between the registered commit and the run:** `git diff 76e80e6 4280cf1 -- src tests tools` is PR #61 only. It adds `bigram_matched_lexicon` (an addition only; `stratified_matched_lexicon` is untouched), the H-A5-09 slot, H-A5-03's closed pair list (which includes H-A5-06 to -08), and report wording. No computation of these runs changed, as the outcome files say. This PR changes nothing under `src/`, `tests/`, `tools/`, `.github/` or `data/`.
- **Not read (blinding respected):** KN Zg 57/58, `data/heldout.txt`, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna. Linear A was read only through `aegean.corpus.load` (training split).

## Summary
**The registered results stand.** Outcome A for all three pairs is the label the decision rule gives. Each prediction is met, and the runs followed the frozen files with no deviation. Every number I checked reproduces exactly. The batch arithmetic and the closure of H-A5-03 are right. Confidence: high.

**One request blocks the merge (R1), and it is about wording only.** The descriptive comparison of the Greek-control row under M1 and M2 is summarised as "mostly disappears" and "largely a property of M1['s licences]". For English the figures do not show that, and the comparison cannot attribute the change to M1's licences. The text appears in five places, one of them an append-only research-notes entry (still editable inside this PR, not after the merge). No p-value, outcome or registered reading is affected.

## Checks

### The runs against the frozen hypotheses
- **Timing.** H-A5-06 to -08 were merged at `4280cf1` (23:30:54 +0200). The outcome commit is `4e2340d` (23:37:51). Three runs of about 60 s each fit in that interval. *Confidence: high that the runs followed the merge. That each command ran only once rests on the author's statement and cannot be checked from the repository.*
- **Null and seeds:** `stratified_matched_lexicon`, K = 1,000, `random.Random(20261114)` in sequence, as registered. The control is the NeuroDecipher set, with 881 words eligible, as registered. The A1.14 seed is 20261115, and α = 0.05. M2 runs at its default `M2Rules` (max distance 0.25), as registered.
- **The decision rule.** p1 > α and p2 > α for every pair, so every pair is A on the raw values, and the batch correction cannot change an A.
  - BH over the six pair p-values (0.8711, 0.7802, 0.3546, 0.9461, 0.9321, 0.6713) gives 0.9461 for all six, as reported.
  - No earlier outcome changes.
  - The batch count is 6, and H-A5-03's closed list matches the six pairs.
- **Predictions and readings.** A was predicted for all three, and it is met.
  - Hebrew is read as "M2 as uninformative as M1", with the caveat that an A under M2 is weaker (review N4 of PR #60). That caveat is appropriate.
  - English and Turkish are read as "as intended for an unrelated language". No p2 ≤ α occurred, so the pre-registered false-positive reading does not arise.

### Numbers (independent recomputation)

| Quantity | Outcome files | Independent |
|---|---|---|
| Hebrew: real, false-positive rate, excess, p1 | 0.320, 0.352, −0.032, 0.946 | 0.3201, 0.3517, −0.0316, 0.9461 |
| Hebrew: lower-tail p; hits; null hits | 0.073; 121; 133 | 0.0729; 121; 132.9 |
| Hebrew control: excess, p; at Linear A's lengths | +0.006, 0.386; −0.001 | +0.0063, 0.3856; −0.0014 |
| Hebrew: D, p2 | −0.030, 0.938 | −0.0302, 0.9381 |
| English: real, false-positive rate, excess, p1 | 0.735, 0.745, −0.010, 0.716 | 0.7354, 0.7451, −0.0096, 0.7163 |
| English control: excess, p; at Linear A's lengths | +0.019, 0.139; +0.022 | +0.0193, 0.1389; +0.0220 |
| English: D, p2 | −0.032, 0.932 | −0.0316, 0.9321 |
| Turkish: real, false-positive rate, excess, p1 | 0.717, 0.725, −0.009, 0.671 | 0.7169, 0.7254, −0.0085, 0.6713 |
| Turkish control: excess, p; at Linear A's lengths | −0.003, 0.589; −0.004 | −0.0027, 0.5894; −0.0038 |
| Turkish: D, p2 | −0.005, 0.584 | −0.0047, 0.5844 |
| BH-adjusted pair p (all six) | 0.946 | 0.9461 |
| Post hoc re-weighted D, p (Hebrew, English, Turkish) | −0.030, 0.921; −0.031, 0.924; +0.000, 0.513 | byte-identical JSON on rerun |

The per-source, by-length and stability figures in the outcome files match the generated reports.

### Claims follow from the registered outcome or are labelled
- The outcome labels, the p-values, "as predicted", the batch, and "M2 is uninformative for all three lexicons" all follow from the registered rules.
- The limits are stated: Test 1 is conservative under M2 (N4 of PR #60), and part of the input can never match for Hebrew (N2). Both are stated plainly. This is the right handling, and it keeps an A under M2 from being over-read.
- The post hoc class re-weighting is labelled post hoc, unregistered and non-deciding, and its code is committed. That is correct.
- **The Greek-control comparison between methods: see R1.**

### Circularity
- **Lexicons:** Strong's Hebrew (openscriptures), English from WordNet/CMUdict, Turkish from Zemberek-NLP ranked by FrequencyWords. None is derived from an Aegean source.
- **Classes:** the Dolgopolsky classes come from LingPy's DOLGO table, checked against the LingPy source in the PR #60 review.
- **Readings:** Linear A is read in conventional Linear B values (L1, stated). The control is the NeuroDecipher Linear B–Greek data.
- **Null:** built only from each real lexicon's own positional letter frequencies.
- **Threshold:** fixed on uniform random Linear B strings, not on either input.

No value or reading here was derived from a lexicon under test. *Confidence: high.*

### Literature
- The outcomes make no claim about the language of Linear A, and they say so.
- **Literature on Dolgopolsky-class matching:** it has long shown that class matches arise often by chance, so any significance claim needs a permutation baseline. That is the practice in Baxter & Manaster Ramer 2000 ("Beyond lumping and splitting: probabilistic issues in historical linguistics") and Turchin, Peiros & Gell-Mann 2010 ("Analyzing genetic connections between languages by matching consonant classes", *Journal of Language Relationship* 3). An M2 result at or below chance against matched pseudo-lexicons agrees with that literature.
- **The difference here:** this benchmark compares with generated pseudo-lexicons, not with permuted real word lists (Kessler 2001, *The Significance of Word Lists*). That is why letter co-occurrence remains a candidate confound. The outcome files name it, and H-A5-09 is meant to address it.
- I cite these from memory, not at first hand. *Confidence: medium-high; not a blocker.*

## Required change

**R1. The M1-versus-M2 Greek-control comparison is overstated, and its cause is attributed beyond what the comparison can show.**

*Where:*
1. the bold bullet "The unrelated lexicons' advantage on Greek words is largely a property of M1", in "What follows" of all three outcome files;
2. H-A5-07's outcome: "Part of what made unrelated lexicons beat noise on Greek words under M1 is M1's own licences, not only the lexicons' letter structure";
3. `docs/benchmark.md`: "so it is partly a property of M1's licences" (unlabelled);
4. the new `research-notes.md` entry: its heading "the Greek-word advantage is largely M1's", and the bullet "mostly disappears under M2";
5. the PR description bullet, for consistency.

*What the figures show* (control excess over length-stratified noise; M1 from the H-A5-04/-05 outcomes, M2 from this PR):

| Lexicon | M1 raw | M2 raw | M1 at Linear A's lengths | M2 at Linear A's lengths |
|---|---|---|---|---|
| English | +0.033 (p 0.015) | +0.019 (p 0.139) | +0.028 | +0.022 |
| Turkish | +0.032 (p 0.017) | −0.003 (p 0.589) | +0.022 | −0.004 |

- **For Turkish the advantage does disappear.** For English it shrinks by about two-fifths raw, and by about a fifth at Linear A's lengths, the form Test 2 uses. "Mostly disappears" and "largely" do not describe English.
- **"Neither does clearly" rests on p crossing 0.05.** English moves from 0.015 to 0.139. That is not evidence that the advantage is gone, and the change between methods was not tested. The two runs share the control and the pseudo-lexicon seed stream.
- **The change cannot be attributed to M1's licences.** M1 and M2 differ in more than the licences:
  - the class system: d with t, affricates with velars, v with w (H-A5-06, Method);
  - the lexicons' form sets: the Dolgopolsky conversions give different skeleton sets; the 502nd English skeleton comes from *marvel* under M2 and from *hurtle* under M1, and the Turkish from *koyultmak* against *yankılamak*;
  - the matching rule: edit distance 1/4 against exact match after licences;
  - control eligibility: 881 words against 902.

  "Not only the lexicons' letter structure" is therefore not separable here either: under M2 the lexicons' letter structure itself changed. "M1 as a whole" is defensible as a reading; "M1's licences" would need an ablation, for example M1 without its licences, or M2 on M1's classes.
- **An alternative is not mentioned.** Under M2 the one lexicon still ahead of noise on Greek words is English, the Indo-European one. H-A5-02 named that pull on the control in advance, and the review of PR #57 (N2) raised it. These are point estimates only, but the outcome should not leave the method-licence reading as the only one.

*Suggested wording* (any equivalent is fine):
- In the outcome files: "**Descriptive, my reading (rule 5):** under M2 the unrelated lexicons' advantage on Greek words disappears for Turkish (+0.032 → −0.003) and shrinks for English (+0.033 → +0.019; at Linear A's lengths +0.028 → +0.022); the change is not tested. M2 differs from M1 in its licences, its classes, its lexicon conversions and its matching rule, so this does not say which of them carried the M1 advantage. English, the Indo-European lexicon, is the one that keeps part of it."
- The same, shortened and labelled, in `docs/benchmark.md` and in the research-notes heading and bullet.

*Why blocking:* the research-notes entry becomes append-only once merged, and `docs/benchmark.md` is the summary Marius reads. The current text states a numerically inaccurate summary for one of two lexicons and a causal attribution the design cannot support. *Confidence: high on the figures; the IE point is a reading, not a measurement.*

## Notes (non-blocking)

- **N1. Two-sign groups that can never match (H-A5-06 outcome, N2 point).**
  - "Its 83 two-sign groups (130 two-class groups in all) can never match" is slightly off. 81 of the 83 two-sign groups have two classes. Two have three (a sign with two consonants) and can match, which is why the null's two-sign rate is 0.001 and not 0.
  - The 130 is right: 81 + 45 + 4.
  - Suggested: "81 of its 83 two-sign groups (130 two-class groups in all)".
- **N2. "N4 above" in the H-A5-06 outcome refers to a point below.** Also, N4 places M2's shortfall on random strings at three and four *classes*, while the sentence speaks of three- and four-*sign* groups. The two are related but not the same; say "classes" or drop the cross-reference.
- **N3. The threshold calibration reproduces what it prints, but the 1/3 range applies to English only.**
  - At 1/4 the script gives real 0.269, 0.553 and 0.461 and nulls 0.296, 0.590 and 0.494, which reproduces the quoted figures exactly.
  - At 1/3 it prints class-count rates for English only: 0.93 for two classes and 0.99 for three, which reproduces "0.93–0.99".
  - With the same strings, Hebrew gives 0.97 and 0.96, and Turkish 0.90 and 0.96. The `M2Rules` comment's "0.93–0.99 … match any of the three lexicons" is exact for English only; over the three the range is 0.90–0.99. The saturation conclusion is unaffected.
  - The script's docstring says it was committed after the fact. I cannot verify that it is the procedure originally used, only that it reproduces the quoted figures. A later plain PR could print all three lexicons by class count.
- **N4. Hit rates over the groups that can match (N2 of PR #60) are not reported.**
  - For Test 1 none are needed. A group that cannot match scores 0 under the real lexicon and under every pseudo-lexicon, so restricting the input rescales every hit rate by the same factor and leaves p1 unchanged.
  - The excess grows by the inverse share: Hebrew −0.032 × 378/240 ≈ −0.050 over its 240 matchable groups; English and Turkish by 378/370.
  - One sentence saying this would close the point. Test 2 would change, because the control would be restricted too; that remains optional and descriptive.
- **N5. Review N3 of PR #60** (the Hebrew null shares on average 268 of the real 414 three-class forms, so Hebrew's tests work through about 150 differing forms) is not carried into the outcome file. It is a one-line lexicon-side fact, worth adding beside N2.
- **N6. H-A5-09 re-runs.** The research-notes "Next" re-runs the six pairs under H-A5-09 as disclosed checks under the less-favourable rule. As N8 of PR #60 says, the H-A5-09 review should check that it names those pairs and applies H-A5-03, Part 1, point 4.

## Process
- **Description:** its first line is "**Review-gated: `docs/reviews/H-A5-06-outcome-review.md`**", which is this file.
- **Files touched:** no rule file, held-out file or enforcement code. `research-notes.md` and the plan change only by appended lines. `docs/for-marius.md` gains an information-only item.
- **CI:** before this review, CI (`test`) failed for the missing review, as expected. With this verdict it will keep failing until a re-review approves.
- **After R1:** once the author has fixed R1, a reviewer (this instance or a new one) appends a re-review to this file.

Verdict: CHANGES REQUESTED

---

## Re-review

### Re-review 1 (2026-11-18)

- **Reviewer:** a separate Claude instance (fresh subagent). I wrote neither this PR, the fix commit, nor the first review above. I was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #62 at `47e1f70` ("fix R1 … N1-N5"), against the first review at `62c51c0` and `main @ 4280cf1`. I read the whole diff against `main`, not only the fix commit.
- **Rerun:**
  - **New figures in the fix**, with my own scratch scripts (not committed) over `aegean.corpus.load` (training split), `M2`, the lexicon registry and `tier1.matched_lexicons`. Results under "New claims" below.
  - **The test suite:** 335 passed, 4 skipped.
  - **The guardrail script from `main`** (`git show origin/main:tools/check_guardrails.py`), with the current PR body: before this re-review it fails only on the first review's CHANGES REQUESTED verdict.
- **Not read (blinding respected):** KN Zg 57/58, `data/heldout.txt`, the held-out split, Kanta et al. 2025, *Anetaki II*, Kanta–Perna.

#### R1 — resolved
*Confidence: high.*

All five places named in R1 are reworded:
1. "What follows" in all three outcome files now uses the suggested wording. It is labelled descriptive (rule 5), says the change is not tested, lists the four ways M2 differs from M1, and names the English (Indo-European) alternative.
2. H-A5-07's per-pair bullet no longer attributes the change to M1's licences. It gives both forms of the figure (raw, and at Linear A's lengths).
3. `docs/benchmark.md`: "gone for Turkish … smaller for English … the change is not tested … the cause is open".
4. `research-notes.md`: the heading claim is removed, and the bullet is reworded the same way. The edited entry is new in this PR; against `main` the file changes only by appended lines (checked with `git diff origin/main`).
5. The PR description is reworded the same way.

I grepped the whole PR diff for "largely", "mostly disappear", "partly a property" and "licences". No assertion of the old kind remains outside this review file. The figures quoted match the M1 outcomes (H-A5-04: +0.033, p 0.015, +0.028 at Linear A's lengths; H-A5-05: +0.032, p 0.017, +0.022) and the M2 reports.

#### New claims in the fix, checked
| Claim (where) | Check | Result |
|---|---|---|
| Hebrew three-sign groups 0.363 against 0.381, four-sign 0.512 against 0.654 (H-A5-06) | generated report, "By length" | matches |
| Hebrew: 130 two-class groups never match, 81 of the 83 two-sign groups among them; the groups of six or more classes never match either (H-A5-06 to -08, N2) | sign count × class count over the 378 eligible groups; real Hebrew hits by class count | 81 (2,2) + 45 (3,2) + 4 (4,2) = 130, all 0 hits; 2 two-sign groups have 3 classes; 6 or more classes: 8 groups, 0 hits; 5 classes: 19 groups, 2 hits (so "six or more" is the right cut-off) |
| Dropping groups that can never match changes no p1 (N2) | argument | correct: a constant zero in every lexicon's hit count leaves every rank unchanged |
| On uniform random strings the real lexicons trail their pseudo-lexicons "mostly at three and four consonant classes" (N4) | calibration strings (seed 99), 20 pseudo-lexicons, gap by class count | Hebrew −0.020 (3), −0.008 (4); English −0.026, −0.015; Turkish −0.018, −0.022. At two classes English and Turkish are *ahead* (+0.009, +0.011). "Mostly at three and four" holds |
| Threshold 1/3 saturation 0.90–0.99 across the three lexicons (outcome correction, research-notes correction, `m2.py` comment) | same strings, threshold 1/3, by class count | Hebrew 0.972, 0.964; English 0.929, 0.991; Turkish 0.901, 0.955. Range 0.90–0.99: correct |
| The Hebrew null shares on average 268 of the real 414 three-class forms (H-A5-06) | all 1,000 registered pseudo-lexicons (seed 20261114) | 414 is right; mean 266.8 (range 247–287). See note M3 |

#### Other changes in the fix
- **`src/aegean/benchmark/m2.py`:** the change is to a comment only (the 1/3 saturation range). So the first review's "This PR changes nothing under `src/`" no longer holds, but nothing that is computed changes. The file is not a rule file or held-out lock code, and the tests pass.
- **The first review's report** is recorded on the PR as a comment headed "recorded unedited", as CLAUDE.md requires.
- **H-A5-08's per-pair bullet** ("Under M2 both advantages are gone (−0.009 … −0.003 …)") is a statement about point estimates, and it is true of them. It makes no causal claim, so R1 did not cover it and it needs no change.

#### Notes (non-blocking; none affects an outcome, a p-value or a reading)
- **M1. Date of the new research-notes entry.** It is headed "2026-11-19", but the fix commit is dated 2026-11-18 23:54 +0200 (21:54 UTC). The entry becomes append-only on merge, so a later entry can correct the date if it matters.
- **M2. Heading of the review-points section.** In all three outcome files, the items taken from the review of PR #62 sit under the heading "Points from the review of PR #60 …, seen before the run":
  - the N3 correction;
  - the Hebrew null overlap;
  - the added sentence in N2.

  They were not seen before the run. Each one is labelled with its source, so a reader can tell, but the heading is no longer exact. A later plain PR could split the section.
- **M3. Hebrew null overlap.**
  - Over the 1,000 registered pseudo-lexicons the mean is 266.8 shared forms (range 247–287), not 268. The figure comes from the PR #60 review, which probably used another sample; the difference is immaterial.
  - "Close to the lexicon itself" fits a sharing of about two-thirds less well than "shares about two-thirds of its three-class forms". It is a matter of wording only.

#### Process
- The description's first line still names this file.
- No rule file, held-out file or enforcement code is touched.
- `research-notes.md` and the plan change only by appended lines against `main`.
- With this verdict, the guardrail script from `main` should pass, and CI (`test`) merges the PR.

Verdict: APPROVE
