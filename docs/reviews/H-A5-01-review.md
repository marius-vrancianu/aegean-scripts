# Independent review — H-A5-01 (Tier 1 protocol; first run M1 × Hebrew verbs), PR #45

- **Reviewer:** a separate Claude instance (fresh subagent, 2026-11-14) that did not write H-A5-01, the benchmark code or any part of this PR. Required by `CLAUDE.md` → Merging (review-gated). It was given the PR number and the fixed review prompt only.
- **Reviewed:** PR #45 at `d85df9c` against `main @ bbe9c69`: `hypotheses/H-A5-01.md`, `hypotheses/TEMPLATE.md`, the plan, research-notes and inbox changes; and the code the hypothesis names (`src/aegean/benchmark/`, `src/aegean/corpus/load.py`).
- **Rerun:** the test suite (241 passed, 4 skipped); the guardrail script from `main` (fails only for the missing review, as expected); every control-side and lexicon-side figure in the file (table below).
- **Not done, on purpose:** no hit rate of any lexicon on Linear A sign-groups was computed (that is the registered run). I computed only the counts of Linear A sign-groups, which the file already lists as seen. No held-out material was read.
- **Not checked:** the synthetic-run figures (0.471 / 0.480 on 945 random strings); the 20,775-string port comparison (it needs the Finding 001 word list; only its committed part ran, in the test suite); the statement that no Linear A hit rate was seen before registration. That statement cannot be verified from the repository. It is consistent with what is there: no `experiments/A5.17/` directory, no test that runs the benchmark on the real corpus.

## Summary

The design is sound and the file is honest about what was seen. Three things in the hypothesis file and one in the template must change before the merge, because the file is immutable afterwards and Part 1 binds every later Tier 1 run. None changes the first run's design or its constants.

## Required changes

### R1. The decision rule leaves one case without a label
*Confidence: high (read from the table; confirmed in the code).*

- Outcomes A and B are defined on the raw p1 and p2. Outcome C needs raw p1 ≤ α, raw p2 ≤ α **and** a Benjamini–Hochberg adjusted pair p ≤ 0.05 (Benjamini–Hochberg: the standard correction that keeps the expected share of false discoveries in a batch below a set level).
- A pair with both raw values ≤ α whose adjusted value is above 0.05 is therefore neither A, B nor C. Example: five pairs with pair p-values 0.04, 0.04, 0.9, 0.9, 0.9 give adjusted values 0.10, 0.10, …; the first two have no outcome. The same hole swallows an earlier C that a later pair pushes above 0.05.
- With one pair it cannot happen, so the first run is not affected. The second pair is.
- `tier1.label(0.04, 0.04)` returns C whatever the batch is; `bh_adjust` exists but the runner never calls it.
- **Fix in the file:** say which outcome that case gets (B, "passes both tests alone but not after the batch correction", is the natural choice), and say in one line that A and B are decided on raw values.
- Follow-up, not for this PR: before a second pair is registered, the runner should take the batch and apply the correction itself, so the generated report cannot print a C that the protocol does not grant (plain PR).

### R2. What Test 2 removes is overstated
*Confidence: medium-high (argument, supported by one check; not measured on Linear A).*

- The file says D "removes what Linear A and the control share". It removes a shift that is **equal** on both inputs. A real lexicon differs from pseudo-lexicons in structure (the file's own example: adjacent identical letters, 0.14 against 0.18 of forms). How much that structure helps or hurts depends on the input's own sign patterns, and Linear A sign-groups and Greek words in Linear B spelling differ in those. The control's excess is not constant even across lengths (+0.036 at two signs, +0.011 at five or more).
- Consequence: p2 is calibrated against the null "the real lexicon behaves like a pseudo-lexicon". It is not calibrated against "the real lexicon belongs to a real but unrelated language". An outcome C, or the second kind of B, can arise from that difference alone.
- The file already limits C to "qualifies for Tier 2 (… unrelated-language lexicons)", so the conclusion drawn is safe. The reason given is not.
- Check I ran (control only): the 902 control words split at random into two halves, one used as input and one as control, 200 times, real Hebrew lexicon. Test 2 was ≤ 0.05 in 4% of splits (median p 0.48). So a shift common to two samples of the same kind does cancel. The check says nothing about two inputs of different kinds.
- **Fix in the file:** one sentence under "Why a second test" or in the meaning of outcome C: Test 2 assumes the lexicon's non-linguistic advantage is the same size on both inputs; where it is not, p2 can be small without any relationship, and only Tier 2's unrelated-language lexicons can separate the two.

### R3. One figure is wrong by rounding
*Confidence: high (rerun).*

- "What I already know": the control's excess at four signs is given as +0.018. The rerun gives +0.0189, so +0.019. The other three (+0.036, +0.022, +0.011) are right.

### R4. The new template line, left unedited, opens the held-out lock
*Confidence: high (tested against the loader's own pattern).*

- The loader releases the held-out split to a merged hypothesis whose Type line matches `**Type:** confirmatory` followed by a word boundary (`load.CONFIRMATORY_RE`).
- The template line added here reads `- **Type:** confirmatory / exploratory (…)`. That line matches the pattern as it stands. A hypothesis that copies the template and forgets to delete one option would count as confirmatory.
- H-A5-01's own line (`exploratory (…)`) does not match; I checked.
- The weakness is in the loader's pattern, which predates this PR, but this PR adds the text that triggers it.
- **Fix in this PR:** make the template's placeholder a string the pattern rejects, for example `- **Type:** exploratory / confirmatory (choose one; …)`.
- Follow-up, not for this PR: tighten the pattern in `load.py` so that the line must hold `confirmatory` and nothing else before any bracket. That is a strengthening of a rule file: its own review-gated PR, no instruction from Marius needed.

## The four required checks

### 1. Null model — adequate
- **Matched pseudo-lexicons.** Rerun: all 1,000 have exactly 664 forms after M1's expansion (real: 502 skeletons → 664). M1 compares sign-groups with the expanded set only, so this is the right quantity to equalise. They average 457 forms before expansion against the real 502, as expected, since random forms collide less.
- **Same 1,000 for Linear A and the control**, one seeded stream. This is what makes D comparable across inputs.
- **Greek control.** Present, as guardrail 2 requires. Limits: see R2 and note N3.
- **Random sign strings and the Finding 001 null** are reported and decide nothing. Correct: the first compares sign-groups with noise, the second is known to be unfair.
- Small point: the generator rejects a form that would overshoot the target size, which slightly favours forms with fewer variants at the very end of each draw. Negligible at 664 forms. No change asked.

### 2. Power check — passes
- Smallest attainable p for both tests is 1/1001 ≈ 0.000999 < 0.05 (the real lexicon above all 1,000 pseudo-lexicons). Ties count against the real lexicon, which is conservative.
- Under the batch correction the smallest value stays usable up to 50 pairs (0.000999 × 50 = 0.04995). The file says so and caps the protocol there. Correct.
- It is reachable in practice: on the control the pseudo-lexicons' spread is 0.013 (rerun), so the highest of 1,000 sits near +0.04 above their mean, well below the ceiling of 1.
- The file states what Tier 1 cannot show (no known positive; an outcome A is about the method, not about the language). That is the honest reading and it is stated before the run.

### 3. Decision rule and batch count — one gap (R1), otherwise sound
- α, both tests one-sided, pair p = max(p1, p2): the maximum of two valid p-values is a valid, conservative p for "both hold". No correction between them is needed, as the file says.
- Batch: every pair ever run under the protocol, failures included; this pair is 1 of 1. Running count of A5 hypotheses: 1. Finding 001's earlier run of the same pair is disclosed as prior knowledge, not hidden.
- Only the primary input decides; per-source and by-length tables are descriptive. Stability figures are reported, not decided on. Deviations rule is present.
- The correction assumes the pairs' p-values are not negatively dependent. Pairs share inputs and pseudo-lexicon seeds, so positive dependence is the plausible case. Acceptable; worth one clause when the batch grows.
- Prediction (outcome A) is stated in advance.

### 4. "What I already know" — complete as far as I can check
- Every figure in it that can be rerun without Linear A hit rates reproduces (table below), bar R3.
- It discloses the uncomfortable parts: the null and Test 2 were designed after seeing control results; the pass criterion for the calibration was set after seeing the figures; the Finding 001 run included documents now held out, which is why the held-out split is declared unusable for this question.
- Two things it could add, neither required: the control's excess re-weighted to Linear A's lengths (+0.024, sd 0.0145; it follows from figures already listed), and the author's prior from the literature survey that a Semitic reading is a minority position, which also feeds the prediction.

## Figures rerun

| Claim in the file | Rerun |
|---|---|
| Lexicon: 502 skeletons, 664 after expansion | 502, 664 |
| Control: 918 distinct words, 902 eligible | 918, 902 |
| Eligible Linear A sign-groups: 414 primary; 321 / 400 / 195 | 414; 321 / 400 / 195 |
| Control, matched null: real 0.532, null 0.512 (0.486–0.538), excess +0.020, p 0.064, lower-tail p 0.944 | 0.5322, 0.5121 (0.4856–0.5377), +0.0201, 0.0639, 0.9441 |
| Null sd on the control: 0.013 | 0.0130 |
| Control by length, excess: +0.036, +0.022, +0.018, +0.011 | +0.0360, +0.0218, **+0.0189**, +0.0110 |
| Finding 001 null on the control: −0.029, lowest 2.5%; about 743 forms | −0.0288, lower-tail p 0.025; mean 744 |
| Adjacent identical letters: real 0.14, pseudo-lexicons 0.18 | 0.139, 0.180 |
| Finding 001 figures (0.800, 0.828, 0.734, 0.394 / 0.424, 0.908, 0.935, 0.747) | agree with `findings/001-yadiktu-null-test.md` |

Script: control and lexicon side only, protocol seeds, `main @ bbe9c69` code.

## Notes (no change required)

- **N1. Code and file agree** on the sign-group definition, eligibility, the length bins, the re-weighting, the leave-one-out scaling in Test 2, all seeds and constants.
- **N2. Rule 4 (known script first).** The validation is a false-positive calibration plus synthetic known-answer tests. There is no known positive at Linear A's scale. For a protocol whose strongest outcome is "qualifies for Tier 2", and which says so, I accept this. It would not be enough for any claim of relationship.
- **N3. The control is not perfectly Semitic-free.** Mycenaean Greek has a few words usually taken as Semitic loans (ku-ru-so "gold", ki-to "tunic", sa-sa-ma "sesame", ku-mi-no "cumin"; consensus as far as I know, from memory, not checked against a source here). They are nouns, the lexicon is verbs, and they are a handful in 902. Negligible; if anything they make Test 2 slightly harder to pass.
- **N4. Layout.** Part 2's sections use the same heading level as "Part 2" itself, and "Null model(s)" appears twice. Cosmetic.
- **N5. Other files in the PR.** `research-notes.md` is appended to only. The plan keeps A5.13 open with an annotation, which is right while Tier 2 is unwritten. The inbox change removes the settled template item. No rule file is touched; nothing in the PR was prompted by fetched content that I can see.
- **N6. Rule 5.** R2 and N3 are my reasoning, not results. R2's check is the only measured part.

## Re-review

Fix R1–R4 in the PR. A reviewer then appends a re-review below this line.

Verdict: CHANGES REQUESTED

## Re-review, 2026-11-14

- **Reviewer:** a separate Claude instance (fresh subagent) that wrote neither H-A5-01, the benchmark code, the fixes, nor the first review above. Given the PR number and the fixed review prompt only.
- **Reviewed:** PR #45 at `449eaa5` (branch head, same as the remote) against `main @ bbe9c69`; the fix commit `ba936de..449eaa5` line by line; the whole of `hypotheses/H-A5-01.md` again as it will be frozen; `src/aegean/benchmark/{tier1,nulls,inputs,lexicons}.py` and the gate in `src/aegean/corpus/load.py`.
- **Not done, on purpose:** no hit rate of any lexicon on Linear A sign-groups was computed. From Linear A I computed only the counts of eligible sign-groups and their length bins, which the file lists as seen. No held-out material was read.

### The four requested changes

| | Status | How checked |
|---|---|---|
| **R1** decision rule | Fixed. Confidence high. | Read as a case table: both raw p > α → A; exactly one ≤ α → B; both ≤ α and adjusted pair p > 0.05 → B; both ≤ α and adjusted ≤ 0.05 → C. The four cases are exhaustive and exclusive. The file now says A and the first two kinds of B rest on raw values, and which label changes are possible later (C → B, third-kind B → C). Both directions are real under Benjamini–Hochberg (the correction that keeps the expected share of false discoveries in a batch below a set level): `bh_adjust([0.04, 0.04, 0.9, 0.9, 0.9])` gives 0.10 for the first two; adding enough pairs with very small p brings them back under 0.05. |
| **R2** what Test 2 removes | Fixed. Confidence high that the text now says the right thing; the underlying point remains an argument, not a measurement. | The sentence now reads "the part of it that is **equal** on Linear A and on the control", and a new paragraph states the assumption, its failure mode (small p2 with no relationship), what p2 is calibrated against, and that only Tier 2 separates the two. Outcome C's meaning is unchanged and consistent with it. |
| **R3** rounding | Fixed. Confidence high. | Rerun: +0.0189 at four signs; the file says +0.019. |
| **R4** template line | Fixed. Confidence high. | `load.CONFIRMATORY_RE` does not match `hypotheses/TEMPLATE.md` as it now stands, nor H-A5-01, nor any other file under `hypotheses/`; it still matches the old wording, so the test is a real one. The template's own description of the gate ("Type line begins with the word confirmatory") agrees with the pattern. |

The fix commit touches only `hypotheses/H-A5-01.md`, `hypotheses/TEMPLATE.md`, `research-notes.md` (one entry appended, nothing earlier edited) and `docs/for-marius.md` (the two follow-ups). The first review's text is untouched by the author. No constant, seed, test or threshold of the protocol changed between `d85df9c` and `449eaa5`; the other edits are the two additions to "What I already know" that the first review suggested and the heading levels of Part 2.

### The four required checks, again on the final text

1. **Null model — adequate.** Rerun with the protocol seed: all 1,000 matched pseudo-lexicons have exactly 664 forms after M1's expansion (457 before, on average); one seeded stream serves Linear A and the control. Greek control present (guardrail 2). The two other nulls are reported and decide nothing.
2. **Power check — passes.** Smallest attainable p is 1/1001 ≈ 0.000999 for both tests, below α; 50/1001 = 0.04995, so the stated cap of 50 pairs is right. The "roughly 0.03" effect size is labelled approximate and not measured on Linear A; with the control re-weighted to Linear A's lengths the pseudo-lexicons' spread is 0.0145, so 0.03 is about two standard deviations, a fair description.
3. **Decision rule and batch count — sound.** See R1. Pair p = max(p1, p2) is a valid conservative p for "both hold". Batch: 1 of 1; running A5 count 1; the dependence assumption of the correction is now stated. Prediction (outcome A) is stated in advance. Code and file agree on α, K, the seeds (20261114–20261118), the bins, the re-weighting and the leave-one-out scaling.
4. **"What I already know" — complete as far as it can be checked.** It matches and exceeds what the research-notes entry of 2026-11-14 ("A5.17") records as seen, and now also lists the figures that reached the author through the first review and the prior from the literature.

### Figures rerun (independent script, control and lexicon side, `449eaa5` code)

| Claim | Rerun |
|---|---|
| 502 skeletons, 664 after expansion | 502, 664 |
| Control 918 words, 902 eligible | 918, 902 |
| Eligible Linear A sign-groups 414; 321 / 400 / 195 | 414; 321 / 400 / 195 |
| Control: 0.532, 0.512 (0.486–0.538), +0.020, p 0.064, lower-tail 0.944, sd 0.013 | 0.5322, 0.5121 (0.4856–0.5377), +0.0201, 0.0639, 0.9441, 0.0130 |
| Control by length: +0.036, +0.022, +0.019, +0.011 | +0.0360, +0.0218, +0.0189, +0.0110 |
| Finding 001 null on the control: −0.029, lowest 2.5%, about 743 forms | −0.0288, lower-tail p 0.025, mean 744 |
| Adjacent identical letters 0.14 / 0.18 | 0.139 / 0.180 |
| Control re-weighted to Linear A's lengths: +0.024, sd 0.0145 | +0.0237, 0.0145 |
| Split-half on the control: Test 2 ≤ 0.05 in 4% of 200 splits | 3% of 200 with a different seed (median p 0.42); same conclusion |

Test suite: 241 passed, 4 skipped. Guardrail script from `main`: its only complaint before this push was the missing approval.

**Not checked** (as in the first review): the synthetic-run figures (0.471 / 0.480); the full 20,775-string port comparison; the statement that no Linear A hit rate was seen before registration. The last cannot be verified from a repository. It is consistent with it: there is no `experiments/A5.17/` directory, tracked or ignored.

### Notes (no change required)

- **M1. One figure this re-review adds to what the author has seen.** With the control re-weighted to Linear A's length mix, the Hebrew lexicon's one-sided p against the matched pseudo-lexicons is 0.047 (unweighted: 0.064). It follows from the two figures already listed in the file (+0.024 against a spread of 0.0145), so I do not ask for it to be added. Its meaning: at Linear A's lengths the real lexicon already "beats noise" at α on Greek words. That is a measured reason, on a known script, why Test 1 alone must not decide, and it supports the file's design. It does not show that Test 2 is sufficient (R2 stands as stated in the file).
- **M2. Repeated correction on a growing batch.** Re-applying Benjamini–Hochberg each time a pair is added lets labels move in both directions, and the false-discovery guarantee holds for the batch as it stands at any one time, not for the sequence of labels issued along the way. The file discloses the moves and requires the outcome file that causes one to say so. Acceptable for an exploratory protocol whose best outcome is "qualifies for Tier 2". (My reasoning, not a result; rule 5.)
- **M3. Follow-ups, confirmed and two added.** The two already in `docs/for-marius.md` stand (runner applies the batch correction itself; tighten `CONFIRMATORY_RE`). Two more, both plain PRs or strengthenings, neither needed for this registration:
  - the runner refuses a protocol only if `hypotheses/<ID>.md` is missing from the working tree; it does not check that the file is merged on `main`, as the loader does for held-out access. Rule 3 is therefore kept by the agent, not by the code;
  - the docstring of `tier1.py` and the test name `test_difference_test_removes_a_shift_common_to_input_and_control` still carry the pre-R2 wording ("the difference removes it"). The registered text is the authority; the code comments should follow it.
- **M4. Rule 4.** As the first review's N2: no known positive exists at Tier 1, and the file says so. Enough for a false-positive protocol; not enough for any claim of relationship, and the file makes none.
- **M5.** Nothing in the PR touches a rule file, `data/heldout.txt` or the lock code; no guardrail is weakened; nothing in it appears to have been prompted by fetched or third-party text.

### Assessment

R1–R4 are fixed as requested, and the fixes introduced no new problem. The protocol states its null, its power, its decision rule and its batch, and it is candid about what was seen before registration and about what Tier 1 cannot show. It can be frozen.

Verdict: APPROVE
