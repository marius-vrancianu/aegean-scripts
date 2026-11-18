# Independent review — H-A5-06, H-A5-07, H-A5-08 (M2 × Hebrew, English, Turkish; protocol H-A5-03, pairs 4–6), PR #60

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-18). I did not write H-A5-06 to H-A5-08, M2 (PR #59) or any part of this PR. Required by `CLAUDE.md` → Merging (review-gated). I was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #60 at `0511202` against `origin/main @ 76e80e6`: `hypotheses/H-A5-06.md`, `H-A5-07.md`, `H-A5-08.md`, the plan change-log line and the research-notes entry. I read them against `hypotheses/H-A5-01.md` (Part 1), `hypotheses/H-A5-03.md` (Part 1), the H-A5-03 to H-A5-05 outcomes and reviews, and the code the files name (`src/aegean/benchmark/{m2,lexicons,nulls,tier1,batch,inputs}.py`, `tests/test_benchmark_m2.py`).
- **Rerun:**
  - the test suite: 333 passed, 4 skipped;
  - every lexicon-side and input-side figure the files give (below);
  - the registration check `batch.check_registered` in a scratch clone with `main` set to the PR head: H-A5-06, H-A5-07 and H-A5-08 map to protocol H-A5-03;
  - `batch.admit` with stub records: the three pairs enter the H-A5-03 batch as pairs 4–6, with no clash with the M1 pairs;
  - Benjamini–Hochberg on illustrative p-values;
  - an approximate re-run of the threshold calibration on uniform random Linear B strings;
  - LingPy's DOLGO class table, read from the LingPy 2.6.13 source archive as data.
- **Deliberately not done:** I computed no hit rate of M2, with any real or pseudo-lexicon, on Linear A sign-groups or on the Greek control. I read no held-out material. Linear A training-split sign-groups and the control were read through `aegean.corpus.load` and `inputs.linear_b_control` for **input-side counts only** (eligibility, skeleton lengths). This review adds some new input-side and synthetic-string figures (N1, N2). Before this review they were not known to the author, and the outcome files should list them as seen through the review.
- **Cannot be checked from the repository:** that no M2 hit rate was seen before registration. What is there is consistent with that: `experiments/A5.17/results/` holds no M2 file, and `batch-H-A5-03.json` has three M1 pairs.

## Summary
These are short pair files under a protocol that has already been reviewed, and they do what such files should do:
- they state the method and its single free parameter, how the parameter was fixed and on what data;
- they give the lexicon conversions, the eligibility counts and the batch position;
- they fix the reading of each outcome in advance, and say what was and was not seen.

Every figure I could check reproduces. The power check and the batch arithmetic are right. The null is the protocol's, and M2 meets the precondition the stratified null needs (expansion is the identity). Under M2 the equal-shift assumption of Test 2 has a measurable weak point: the Test 2 standardisation is by sign count, but M2's hit rate depends on the number of consonant classes. On my rough estimate the effect is small, and the files' readings of p2 ≤ α already guard against it. I record it as a non-blocking note, with figures, for the outcome files (N1).

## The four required checks

### 1. Null model: sound
*Confidence: high (code read; lexicon side measured).*
- M2 inherits `Method.expand` (identity), so `prepare(real) == real.forms`. `nulls.stratified_matched_lexicon` therefore matches the real lexicon's count of forms at every length, as the files say ("matches the lexicon's own forms at every length"). The precondition check in the null (expansion keeps lengths) is satisfied trivially.
- Lexicon sizes reproduce exactly:

  | Lexicon | Distinct forms | 2 classes | 3 classes | 4 classes | 502nd form from |
  |---|---|---|---|---|---|
  | Hebrew | 428 | 0 | 414 | 14 | (all verbs) |
  | English | 502 | 66 | 194 | 242 | *marvel* |
  | Turkish | 502 | 51 | 166 | 285 | *koyultmak* |

  All three use the 10-class alphabet PTSKMNRWJH.
- **The Dolgopolsky classes are LingPy's.** I checked LingPy 2.6.13 `data/models/dolgo/converter`:
  - K includes the affricates (ts dz tʃ dʒ) with the velar and uvular stops and fricatives;
  - H is ʔ ħ ʕ h;
  - W is w and v;
  - T is t d θ ð;
  - S is s z ʃ ʒ.

  This matches `m2.py`'s table and the three differences from M1 the files name. One detail is handled correctly: in LingPy's table the IPA symbol "ç" (a palatal fricative) is S, but Turkish orthographic ç is /tʃ/, and `TURKISH_DOLGO` rightly sends it to K.
- The z-series is taken at its letter value (S, not K as an affricate), and the q-series is taken as K. Both choices are stated. They apply equally to Linear A and to the control, so they do not bias Test 2 between the two inputs. *Confidence: high.*
- **Null close to a copy, measured.** Mean forms shared with the real lexicon over 100 stratified draws (protocol seed). "Space" is the number of forms possible under the positional letter sets.

  | Lexicon | 2 classes: shared / real (space) | 3 classes | 4 classes |
  |---|---|---|---|
  | English | 57.0 / 66 (90) | 85 / 194 | 31 / 242 |
  | Turkish | 39.6 / 51 (81) | 93 / 166 | 81 / 285 |
  | Hebrew | — | 268 / 414 (810) | 0.2 / 14 |

  H-A5-07's "close to a copy" at two classes holds. The Hebrew three-class figure is not in H-A5-06 (N3).

### 2. Power check: correct
*Confidence: high (recomputed).*
- n = 378 eligible of 545 distinct sign-groups. Skeleton lengths: 2: 130, 3: 162, 4: 59, 5: 19, 6: 7, 7: 1. Control: 881 of 918 eligible. Signs blocking eligibility, counted by occurrence in the distinct groups: *56 23, *79 16, *301 14. All as stated.
- The smallest attainable p is 1/1001 for both tests. Pairs 1–3 have raw pair p 0.8711, 0.7802 and 0.3546 (`batch-H-A5-03.json`). With m = 6 and a single small pair p, the adjusted value is 6p. A raw 0.0083 adjusts to 0.0498, and 1/1001 adjusts to 0.006. "Outcome C needs a raw pair p ≤ 0.0083; attainable" is right. The 50-pair ceiling is far off.
- Not wrong, but worth knowing for the outcome files: with Hebrew, the 130 two-class groups and the 8 groups of six or more classes can never match the real lexicon or any pseudo-lexicon. At most 240 of the 378 carry information. For English and Turkish, the 8 groups of six or more classes never match (N2).

### 3. Decision rule and batch count: correct
*Confidence: high.*
- The decision rule is H-A5-03's (H-A5-01's table, with the stratified null), and no file changes it. The batch is H-A5-03's own; these are pairs 4–6 of 6. "Running count of A5 hypotheses registered: 8" is right (H-A5-01 to H-A5-08).
- The runner accepts the three IDs under H-A5-03 only. M2 refuses `--rules`, so the threshold cannot be varied from the command line. `pair_key` includes the rules, so an M2 run at another threshold would be a new pair, counted in the batch.
- The readings fixed in advance are adequate:
  - Hebrew: a C qualifies for Tier 2 only, and is read against English and Turkish;
  - English and Turkish: any p2 ≤ α is a Test 2 false positive for an unrelated language, and a B with p1 ≤ α only is a lexicon-structure effect.
- The threshold is the method's one free parameter. It was fixed on uniform random strings of Linear B values and the real lexicons, not on Linear A or the control. That is a legitimate pre-data choice.

### 4. "What I already know": complete as far as the repository shows
*Confidence: medium-high. Read against the repository; the author's session is not visible to me.*
- Listed:
  - the M1 outcomes and reviews for the same lexicons;
  - the random-string calibration at three thresholds;
  - the eligibility counts and blocking signs;
  - the lexicon-side two-class coverage (English, Turkish);
  - Turkish's near-pass under M1;
  - an explicit "not seen".
- I found nothing in the repository the author saw and did not list. The new figures below come from this review and should be listed in the outcome files as seen through it.

## Non-blocking notes (for the outcome files; no change needed before the merge)

- **N1. Test 2 standardises sign count; M2's hit rate depends on class count.**
  - *Measured, input side.* Share of eligible groups by skeleton class count, within each sign-count bin:

    | Signs | Linear A (n) | Control (n) |
    |---|---|---|
    | 3 | 2 classes 0.263, 3 classes 0.708 (171) | 2 classes 0.408, 3 classes 0.577 (267) |
    | 4 | 3 classes 0.429, 4 classes 0.512 (84) | 3 classes 0.474, 4 classes 0.422 (327) |
    | 5+ | 5–6 classes 0.65 (40) | 5–6 classes 0.44 (204) |

    Linear A sign-groups have more consonant classes per sign than the Greek words, because the Greek words have more pure-vowel signs.
  - *Measured, synthetic.* At 1/4, the hit rate is sharply non-monotone in class count. With Hebrew on uniform random strings:
    - 2 classes: 0, exact match only, and Hebrew has no two-class forms;
    - 3 classes: about 0.37;
    - 4 classes: about 0.72, through one deletion into the dense three-class space;
    - 5 classes: about 0.01;
    - 6 or more: 0.

    The real − null excess also varies with class count (4,000 uniform strings, 40 stratified draws):

    | Lexicon | 2 classes | 3 classes | 4 classes |
    |---|---|---|---|
    | English | +0.033 | −0.101 | −0.082 |
    | Turkish | +0.049 | −0.075 | −0.070 |
    | Hebrew | 0 | −0.039 | −0.033 |
  - *My estimate (rule 5: a proxy, not a measurement on either input).* Suppose the per-class-count excesses on the real inputs were the uniform-string ones. The class-count mix difference alone would then shift D by about −0.002 (Hebrew) and −0.008 (English, Turkish). That is the conservative direction, and a fraction of the spread of D under M1 (95% range about ±0.035). On real inputs the excess at three or four classes may be positive instead: under M1 both unrelated lexicons were ahead of noise on Greek words. The shift would then be positive and of similar size. So the effect is small and of unknown sign.
  - *Suggested for the outcome files:* report, descriptively, D with the control re-weighted to Linear A's joint distribution of sign count and class count. Say whether any p2 ≤ α survives it. This decides nothing; it shows whether the equal-shift assumption is strained by this specific, measurable difference.
- **N2. Groups that can never match.** Under M2 at 1/4:
  - two-class groups match only exactly;
  - groups of six or more classes cannot reach any lexicon form of at most four classes.

  The outcome files should report hit rates also over the groups that can match at all (Hebrew: 3–5 classes, 240 groups; English and Turkish: 2–5 classes, 370 groups), descriptively. Then a diluted excess is not mistaken for a small one.
- **N3. Hebrew lexicon side.** The stratified Hebrew null shares on average 268 of the real lexicon's 414 three-class forms (the positional space is 810). Its 14 four-class forms are almost never reproduced (0.2 shared). H-A5-06 lists only "428 forms; no two-class forms". This is the Hebrew counterpart of H-A5-07's two-class note: the tests compare the real lexicon with noise mainly through about 150 differing three-class forms.
- **N4. Test 1 is handicapped under M2, by lexicon structure.**
  - On uniform random strings, every real lexicon trails its stratified null: by 0.03–0.04 in the files' calibration, and by 0.02–0.04 in my two approximate re-runs.
  - The gap sits at three and four classes (N1). My reading (rule 5): real forms cluster, so their one-edit neighbourhoods overlap and cover less of the space than scattered pseudo-forms.
  - So a p1 > α under M2 is partly expected from lexicon structure, whatever the input. An outcome A for M2 is weaker evidence that the method is uninformative than the same A was for M1. The files state the figures; the outcome files should state the consequence.
  - H-A5-06's rationale "M2 is stricter" does not by itself predict A. Stricter matching lowers both the real and the null hit rates. The prediction decides nothing, so this is a remark only.
- **N5. The calibration that fixed the threshold is not reproducible from the repository.** No script, seed or length distribution for the "1,000 uniform random strings" is committed, and CLAUDE.md asks every stochastic step to carry its seed. My approximate re-runs bracket the cited figures:

  | Lengths (signs, uniform) | Hebrew | English | Turkish | Stratified nulls |
  |---|---|---|---|---|
  | 2–5 | 0.25 | 0.51 | 0.42 | 0.27 / 0.53 / 0.45 |
  | 2–4 | 0.29 | 0.62 | 0.52 | 0.32 / 0.66 / 0.56 |

  At 1/3, two- and three-class strings match 0.87–1.00. The qualitative claims hold. Suggest committing the calibration script with its seed in the next plain PR, so that the figures cited in these immutable files can be regenerated.
- **N6. Wording of "the strictest value that allows any edit".** It is exact only when both strings have at most four classes. At 1/5, a five-class sign-group already reaches a four-class form by one deletion, which concerns 19 eligible groups. The choice is unaffected; the outcome file could say it precisely.
- **N7. Permissiveness is descriptive, and not comparable with M1.** For M2, `tier1.permissiveness` counts the whole reach set, including strings of five or more classes that no lexicon form has, against a reading space built from the lexicon's lengths. The outcome file should say so, or restrict the count to lengths 2–4.
- **N8. Next protocol revision.** The research-notes entry names a further revision (a co-occurrence-matched null) as next. If these M2 pairs are re-run under it, the PR #55 re-review note M1 applies:
  - the revision must close H-A5-03 to new pairs;
  - it must name every pair run under both protocols, with the less-favourable rule.

  The review of that revision should check this.

## Assessment
The three files register exactly what they say:
- one method with one parameter fixed before any data;
- three lexicon conversions that reproduce;
- the protocol's null and tests unchanged, a correct power check and the right batch position;
- readings of each outcome fixed in advance, with prior knowledge disclosed as far as the repository shows.

The notes concern how to report and read the results (above all N1, N2 and N4), not the registration, so they belong in the outcome files.

Verdict: APPROVE
