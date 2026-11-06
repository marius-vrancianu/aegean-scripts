# Finding 002 — What the arithmetic of Linear A totals can and cannot show (corpus-v0.1)

- **Date:** 2026-11-06.
- **Status:** summary of analysis A2 on the provisional corpus; MIXED (one supported test, two inconclusive, several negatives).
- **Corpus:** corpus-v0.1 (lineara.xyz only, L0; sha256 `bb14ce5c…`). Single source, so everything below must be re-run on corpus-v1.0.
- **Layer:** L0 throughout. No sound values are used.

## Summary
1. **Fraction signs are written in a fixed order** (H-A2-07, pre-registered, **supported**). No pair of fraction signs ever appears in both orders. Over 41 adjacent pairs, C = 1.00 against a null mean of 0.77, p < 0.0001. The evidence is concentrated in six repeated pairs (22 occurrences).
2. **Most totals cannot be checked as transmitted** (H-A2-08, pre-registered, **inconclusive**). Under strict rules only 5 of 37 KU-RO totals are testable. Of those, 2 are exact and 1 is off by one stroke (p = 0.049, between the registered thresholds).
3. **When everything is crunched, totals behave like totals** (exploratory). Under the default scope, 9 of 37 KU-RO totals are exact and 3 are off by one stroke, against 0.48 exact matches expected by chance across the 29 comparable rows (p < 0.0001).
   - **Circularity check:** only one of the 9 exact matches (HT 85a) involves a number that the edition itself marks as damaged. The other "damaged" flags came from damage near the numbers. lineara.xyz's damage marking is incomplete, so unmarked restorations cannot be excluded without GORILA's or Younger's apparatus.
4. **Nearly every mismatch has an observable feature that could explain it.** Lost entries on broken sides (about 10), a running total (HT 127b: 292 = 156 + 136), a scope that catches another section or commodity (4), and two fractional offsets (HT 13: −½; HT 9a: +¾, equal to JE). All of these are post hoc. The scope ideas are pre-registered as H-A2-09, for unseen documents only.
5. **HT 122 does not add up as read** (H-A2-04, pre-registered, **inconclusive**). The subtotals give 31 + 65 = 96, but the grand total reads 97, and its last units touch damage. Side b's KU-RO (65) is not the sum of its surviving entries (15).

## Negative results
- **Totals cannot discriminate between fraction value sets on this corpus.** Corazza et al. 2021 and Schrijver 2014 differ on B, D, K, H, A and the L series. None of these signs occurs in a total whose arithmetic otherwise works. On corpus-v0.1, totals constrain only J and E, which both sets value at ½ and ¼. *Consequence:* H-A2-01/02 (value-set comparisons) cannot be decided by totals here. A confirmatory test needs new material, and the fraction-order test on the sceptre (H-A2-06, registered) is the main remaining route.
- **KI-RO:** none of three simple relations holds in any of 11 KI-RO/KU-RO pairs. The relations tried were: KI-RO = the entries before it; KU-RO = all entries − KI-RO; KU-RO = all entries + KI-RO. This is exploratory and weak, because the KI-RO tablets have not been checked against GORILA.

## What this means
- **The arithmetic works where it can be checked.** It supports the standard reading of KU-RO as "total" and of J = ½. It cannot go much further on the existing corpus: there are too few clean totals, and those few use only the commonest fraction signs.
- **The smallness of the corpus is the binding constraint**, not the method. About 30 tablets carry KU-RO, and roughly 5 to 12 of their totals are cleanly checkable. Any claim resting on Linear A arithmetic beyond J and E needs new texts. The same limitation applies to other claims (cf. A5).
- **Agreement with the literature:** Corazza et al. 2021 (p. 2), citing Montecchi 2009 and 2013, say that "no Linear A inscription containing totals of numeral phrases is without reading or calculation problems". Our counts are consistent with that. A direct comparison with Montecchi's tablet-by-tablet catalogue awaits access to those papers.

## Hypothesis accounting (A2)
| ID | Registered | Run | Outcome |
|---|---|---|---|
| H-A2-04 | 2026-11-04 | 2026-11-05 | inconclusive |
| H-A2-07 | 2026-11-04 | 2026-11-05 | supported |
| H-A2-08 | 2026-11-05 | 2026-11-05 | inconclusive |
| H-A2-06 | 2026-11-06 | waits for *Anetaki II* | — |
| H-A2-09 | 2026-11-06 | waits for unseen documents | — |
| H-A2-01/02/03/05 | not registered | — | value sets and KI-RO; no longer blind on corpus-v0.1 after the exploratory census |

Exploratory comparisons (not hypothesis tests) are listed in `experiments/A2/exploratory/README.md`.

## Limitations
- **Single derived source.** lineara.xyz is built from GORILA and Younger, and its damage marks are incomplete.
- **One reader for the GORILA checks**, an LLM counting strokes. A human second check is pending; see `docs/manual-checks/A2-checklist.md`.
- **No known-script validation of the census yet.** The Linear B *to-so* totals (A2.4) wait for DAMOS data.

## Reproduce
```bash
python data/raw/lineara.xyz/fetch.py && python -m aegean.corpus.build
python experiments/A2/run_h_a2_07.py
python experiments/A2/run_h_a2_08.py
python experiments/A2/exploratory/run_census_all.py
```
