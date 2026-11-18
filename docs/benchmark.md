# The benchmark (A5)

Code: `src/aegean/benchmark/`. Layer: L1 (sign-groups read in conventional Linear B values, so every result is conditional on those values holding for Linear A; plan A4 tests that).

**Tier 1 (A5.17)** asks one question of a method that matches Linear A sign-groups to a language's lexicon: how often does it find a language that is not there? **Tier 2** (A5.11–A5.14: can any method find a language that *is* there, at Linear A's size?) is not built yet.

Protocols and decision rule: `hypotheses/H-A5-01.md` (Part 1), and its revision `hypotheses/H-A5-03.md` once registered, which changes only the decision null (length-stratified). Each protocol has its own batch. This page says how the code is organised and how to use it.

## Parts

| Module | What it holds |
|---|---|
| `interface` | `Method`, `Lexicon`, `Match`. A method is a pure function of (sign-group, lexicon). |
| `m1` | Method M1: the Finding 001 root matcher, ported from `experiments/finding-001/original/nulltest.py`. Every licence is a field of `M1Rules`. |
| `m2` | Method M2: Dolgopolsky sound-class skeleton matching, normalised edit distance ≤ 1/4, no claim-specific licences. |
| `lexicons` | Real lexicons converted to the forms a method compares against: Hebrew verb skeletons (Strong's); English verb skeletons (WordNet + CMUdict) and Turkish verb skeletons (Zemberek + FrequencyWords), unrelated-language lexicons; each also in Dolgopolsky classes (`*-dolgo`) for M2. |
| `nulls` | Matched pseudo-lexicons (the decision null), Finding 001 pseudo-lexicons (kept for continuity), random sign strings. |
| `inputs` | Linear A sign-groups through `aegean.corpus.load` (training split); Linear B words of known Greek meaning (NeuroDecipher data). |
| `tier1` | The runner, the report and the command line. |
| `batch` | The registration check and the batch correction (Benjamini–Hochberg over every pair run under the protocol). |

## What a run reports

For one method and one lexicon:

- **Hit rate:** the share of distinct, eligible sign-groups for which the method returns a match.
- **False-positive rate:** the mean hit rate under 1,000 matched pseudo-lexicons. No language stands behind a pseudo-lexicon, so each of its matches is false.
- **Test 1:** is the real lexicon's hit rate on Linear A above the pseudo-lexicons'?
- **Test 2:** is the real lexicon's advantage on Linear A larger than its advantage on Linear B words of known Greek meaning? Greek is not the language under test, so an advantage there measures how real lexicons differ from pseudo-lexicons, not a relationship.
- **Outcome A, B or C** from the two tests and the batch-adjusted pair p (`batch.label`). A would-be C whose adjusted p is above 0.05 is reported as B.
- Descriptive tables: each source separately, by length, lexicon size, random sign strings, the method's degrees of freedom (`docs/guardrails.md`, item 3), and resampling intervals (A1.14).

## The pseudo-lexicon nulls

A method sees a lexicon only after its own lexicon-side licences. M1 lets S be read as T and D and T interchange, so the 502 Hebrew verb skeletons become 664 distinct forms.

- **Matched** (`nulls.matched_lexicon`): 664 forms after the same expansion, with the real lexicon's lengths and its letter frequencies at each position. The decision uses this one.
- **Length-stratified matched** (`nulls.stratified_matched_lexicon`), the decision null of protocol H-A5-03: the same, but filled length by length, so that at every form length it has exactly the real lexicon's number of forms after expansion. The matched null above under-draws short forms (English: 61.7 two-letter forms on average against the real 79), which produced a Test 1 false positive for English (H-A5-02); this null removes that bias by construction.
- **Bigram-matched, length-stratified** (`nulls.bigram_matched_lexicon`), the decision null of protocol H-A5-09 once registered: as the length-stratified null, but letters follow the real lexicon's letter-to-letter transitions (first-order Markov chain). Lexicon side, 100 draws each: it shares about as many forms with the real lexicon as the stratified null does (0.38–0.68 against 0.34–0.69), and its bigram distribution is closer to the real one (total-variation distance 0.10–0.13 against 0.14–0.26). Both nulls already share many forms with real lexicons, because the space of three-letter forms is small (1,000–1,331 strings).
- **Finding 001** (`nulls.pseudo_lexicon`): 502 forms before expansion, overall letter frequencies. After expansion these average about 743 forms, so they offer the method about 12% more targets than the real lexicon does. On the Greek control the real lexicon falls in the lowest 2.5% of this null. It is reported for continuity only.

## Running it

```bash
python data/raw/lineara.xyz/fetch.py
python data/raw/younger/fetch.py --from <clone of the private repository>/Younger   # data/raw/younger/README.md
python data/raw/openscriptures-HebrewLexicon/fetch.py
python data/raw/neurodecipher/fetch.py
python -m aegean.corpus.build_layers
python -m aegean.benchmark.tier1 --method M1 --lexicon hebrew-strong-verbs --protocol H-A5-01
```

Output, all generated:
- `experiments/A5.17/results/<hypothesis>-<method>-<lexicon>.json` and `.md`. The first run, H-A5-01, keeps its original name `M1-hebrew-strong-verbs`. A run takes about two minutes on a PC.
- `batch.json` and `batch.md` (protocol H-A5-01), `batch-H-A5-03.json` and `.md` (protocol H-A5-03): every pair run under that protocol, with raw and adjusted p and the final outcome. `python -m aegean.benchmark.batch [--protocol H-A5-03]` rebuilds them from the results files without running anything.

The results files are the record of the batch: commit them with the outcome file, and never delete one.

**What the runner refuses** (before any computation):
- a hypothesis ID whose file does not exist, is not on `main`, or differs from the version on `main`;
- unless the file is itself a protocol, a file without exactly one line `- **Protocol:** H-A5-01` (or `H-A5-03`);
- a hypothesis that was already run with a different (method, rules, lexicon), or a pair already run under another hypothesis of the same protocol (the same pair may be run once under each protocol);
- a batch of more than 50 pairs (H-A5-01, power check).

If adding a pair changes an earlier pair's outcome (a C becoming B), the runner prints it and `batch.md` lists it. The new pair's outcome file must record it.

## Running a third-party claim

A claim of the form "Linear A is language X, by root matching" is run with its own lexicon and its own licences:

```bash
python -m aegean.benchmark.tier1 --method M1 --lexicon-file claim-lexicon.txt --rules claim-rules.json --protocol H-A5-NN
```

- `claim-lexicon.txt`: one comparison form per line, in M1's consonant classes (H laryngeal, P, K, D, T, S, R, M, N, W, J). Converting a dictionary to these classes is part of the claim; write the conversion as a loader in `lexicons.py` when it is more than a list.
- `claim-rules.json`: any subset of the `M1Rules` fields; the rest keep the Finding 001 values. Example: `{"prefixes": ["A", "JA"], "suffixes": [], "weak_radicals": "WJ"}`.
- Register the pair first, in a short hypothesis file with the line `- **Protocol:** H-A5-01`, stating the method, the lexicon, the rules and what is already known. The runner refuses the run until that file is merged.

## Adding a method

Subclass `interface.Method`: `name`, `eligible`, `match`, `degrees_of_freedom`, and `expand` if the method widens the lexicon. Add it to `tier1.METHODS`. Plan §0.7: no method beyond M1 is added before the protocol is merged.

## Results so far

Live tables: `experiments/A5.17/results/batch.md` (protocol H-A5-01, closed) and `batch-H-A5-03.md` (protocol H-A5-03, length-stratified null).

| Pair | Protocol | Lexicon (method M1 unless stated) | Test 1 (p1) | Test 2 (p2) | Outcome |
|---|---|---|---|---|---|
| H-A5-01 | H-A5-01 | Hebrew verbs | 0.397 | 0.840 | A |
| H-A5-02 | H-A5-01 | English verbs (unrelated) | **0.009** | 0.754 | B, Test 1 only |
| H-A5-03 | H-A5-03 | Hebrew verbs (re-run) | 0.469 | 0.871 | A |
| H-A5-04 | H-A5-03 | English verbs (re-run) | 0.288 | 0.780 | A |
| H-A5-05 | H-A5-03 | Turkish verbs (unrelated) | 0.100 | 0.355 | A |
| H-A5-06 | H-A5-03 | M2 × Hebrew verbs | 0.946 | 0.938 | A |
| H-A5-07 | H-A5-03 | M2 × English verbs | 0.716 | 0.932 | A |
| H-A5-08 | H-A5-03 | M2 × Turkish verbs | 0.671 | 0.584 | A |

Cited outcomes (H-A5-03, Part 1, point 4: the less favourable of a pair's runs): M1 and M2, Hebrew A, English A, Turkish A.

- **Test 1 alone can give false positives.** English passed it under the first null (p = 0.009); the length-stratified null removed that.
- **On Greek words, two unrelated lexicons beat length-matched noise** (English +0.033, Turkish +0.032, both p ≈ 0.015 uncorrected; Hebrew +0.017, p = 0.093). This is a descriptive row, not a tested claim, but it means Test 1 alone is not safe under either null. Under M2 the advantage is much smaller (English +0.019, p = 0.139; Turkish −0.003), so it is partly a property of M1's licences. Never quote a Tier 1 result from Test 1 alone.

## Limits

- M1 is an approximate encoding of one paper's licences (Finding 001, Limitations).
- **H-A5-01's matched null under-draws short forms** (fixed by the length-stratified null of H-A5-03). Lengths are drawn from the real lexicon, but repeated forms are redrawn and short forms repeat most, so the pseudo-lexicons end with fewer short forms than the real lexicon (English: 79 two-letter forms against a null mean of 61.7). For a lexicon with many short forms this tilts Test 1 towards the real lexicon.
- The matched null equalises size and positional letter frequencies, not everything: real Semitic roots avoid adjacent identical consonants more than the pseudo-lexicons do (0.14 against 0.18 of forms). Test 2 exists because of residual differences of this kind.
- The Linear B control comes from the NeuroDecipher data until DAMOS is available (plan A1.10), and is re-run then.
- Tier 1 measures false positives only. An outcome A says the method cannot tell the lexicon from noise; it does not say what language Linear A is not.
