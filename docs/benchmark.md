# The benchmark (A5)

Code: `src/aegean/benchmark/`. Layer: L1 (sign-groups read in conventional Linear B values, so every result is conditional on those values holding for Linear A; plan A4 tests that).

**Tier 1 (A5.17)** asks one question of a method that matches Linear A sign-groups to a language's lexicon: how often does it find a language that is not there? **Tier 2** (A5.11–A5.14: can any method find a language that *is* there, at Linear A's size?) is not built yet.

Protocol and decision rule: `hypotheses/H-A5-01.md`. This page says how the code is organised and how to use it.

## Parts

| Module | What it holds |
|---|---|
| `interface` | `Method`, `Lexicon`, `Match`. A method is a pure function of (sign-group, lexicon). |
| `m1` | Method M1: the Finding 001 root matcher, ported from `experiments/finding-001/original/nulltest.py`. Every licence is a field of `M1Rules`. |
| `lexicons` | Real lexicons converted to the forms a method compares against. So far: Hebrew verb skeletons (Strong's). |
| `nulls` | Matched pseudo-lexicons (the decision null), Finding 001 pseudo-lexicons (kept for continuity), random sign strings. |
| `inputs` | Linear A sign-groups through `aegean.corpus.load` (training split); Linear B words of known Greek meaning (NeuroDecipher data). |
| `tier1` | The runner, the report and the command line. |

## What a run reports

For one method and one lexicon:

- **Hit rate:** the share of distinct, eligible sign-groups for which the method returns a match.
- **False-positive rate:** the mean hit rate under 1,000 matched pseudo-lexicons. No language stands behind a pseudo-lexicon, so each of its matches is false.
- **Test 1:** is the real lexicon's hit rate on Linear A above the pseudo-lexicons'?
- **Test 2:** is the real lexicon's advantage on Linear A larger than its advantage on Linear B words of known Greek meaning? Greek is not the language under test, so an advantage there measures how real lexicons differ from pseudo-lexicons, not a relationship.
- **Outcome A, B or C** from the two tests (`tier1.label`).
- Descriptive tables: each source separately, by length, lexicon size, random sign strings, the method's degrees of freedom (`docs/guardrails.md`, item 3), and resampling intervals (A1.14).

## The two pseudo-lexicon nulls

A method sees a lexicon only after its own lexicon-side licences. M1 lets S be read as T and D and T interchange, so the 502 Hebrew verb skeletons become 664 distinct forms.

- **Matched** (`nulls.matched_lexicon`): 664 forms after the same expansion, with the real lexicon's lengths and its letter frequencies at each position. The decision uses this one.
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

Output: `experiments/A5.17/results/<method>-<lexicon>.json` and `.md`. A run takes about a minute on a PC.

`--protocol` names the merged hypothesis file the run belongs to. A run on Linear A for a (method, lexicon) pair without one is not allowed (CLAUDE.md rule 3); the runner refuses an ID that has no file.

## Running a third-party claim

A claim of the form "Linear A is language X, by root matching" is run with its own lexicon and its own licences:

```bash
python -m aegean.benchmark.tier1 --method M1 --lexicon-file claim-lexicon.txt --rules claim-rules.json --protocol H-A5-NN
```

- `claim-lexicon.txt`: one comparison form per line, in M1's consonant classes (H laryngeal, P, K, D, T, S, R, M, N, W, J). Converting a dictionary to these classes is part of the claim; write the conversion as a loader in `lexicons.py` when it is more than a list.
- `claim-rules.json`: any subset of the `M1Rules` fields; the rest keep the Finding 001 values. Example: `{"prefixes": ["A", "JA"], "suffixes": [], "weak_radicals": "WJ"}`.
- Register the pair first, in a short hypothesis file that cites `H-A5-01` for the protocol and states the lexicon, the rules and what is already known.

## Adding a method

Subclass `interface.Method`: `name`, `eligible`, `match`, `degrees_of_freedom`, and `expand` if the method widens the lexicon. Add it to `tier1.METHODS`. Plan §0.7: no method beyond M1 is added before the protocol is merged.

## Limits

- M1 is an approximate encoding of one paper's licences (Finding 001, Limitations).
- The matched null equalises size, lengths and positional letter frequencies, not everything: real Semitic roots avoid adjacent identical consonants more than the pseudo-lexicons do (0.14 against 0.18 of forms). Test 2 exists because of residual differences of this kind.
- The Linear B control comes from the NeuroDecipher data until DAMOS is available (plan A1.10), and is re-run then.
- Tier 1 measures false positives only. An outcome A says the method cannot tell the lexicon from noise; it does not say what language Linear A is not.
