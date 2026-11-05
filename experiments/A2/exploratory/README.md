# Exploratory census of all accounting markers (corpus-v0.1)

**EXPLORATORY — not a pre-registered test.** Marius requested it on 2026-11-05, after H-A2-08 came out inconclusive. Run by Claude the same day.

- **Scope:** every KU-RO, KI-RO and PO-TO-KU-RO occurrence, including damaged and fraction-bearing rows.
- **Fraction values:** two published value sets, Corazza et al. 2021 Table 8 and Schrijver 2014 as tabulated in Corazza's Table 3.
- **Status of the results:** nothing here confirms anything on corpus-v0.1. Every pattern below is a lead to test on new data, or with a pre-registered rule.
- **Files:** `run_census_all.py` produces `census-all.csv` (one row per occurrence and scope), `kiro-relations-*.csv` and `SUMMARY.md`. The code was committed before the run (`6f41219`).

## Results (primary scope S1 for KU-RO; P1 for PO-TO-KU-RO)

### KU-RO: 37 occurrences
| Outcome | Count |
|---|---|
| exact (sum of entries = total) | **9** |
| near miss (off by exactly one stroke: 1, 10, 100) | **3** |
| mismatch | 17 |
| no entries in scope | 6 |
| no total | 2 |

- **Chance baseline.** Across the 29 comparable rows, reassigning totals at random gives on average **0.48** exact matches, against 9 observed. Permutation p < 0.0001 (10,000 permutations, seed 20261105).
- **Caveat: possible circularity.** Editors (GORILA, Younger, lineara.xyz) sometimes restore damaged numerals using the total. An exact match on a damaged tablet may therefore partly reflect the edition rather than the scribe. Seven of the 9 exact matches are on rows Claude marked "damaged". Two explanations need separating: Claude's damage standard was too cautious, or restorations are doing work. Checking each restored numeral against GORILA's apparatus would separate them.

**Exact:** HT 117a, HT 88 (both clean); HT 104 (needs J = 1/2); HT 11b, HT 25b (KU-RO 52), HT 85a, HT 89, HT 94b, HT 9b.
**Near misses:** HT 119 (+1), HT 94a (−1), HT 102 (−10). Here difference = total − sum.

### What the 17 mismatches look like
Nearly all have an observable feature that could explain them. These explanations are possibilities, not findings.

| Pattern | Rows | Difference (total − sum) |
|---|---|---|
| **Sum too low, and the side has a recorded break or lost text** (consistent with lost entries) | HT 109, 110a, 122a, 122b, 127b (KU-RO 156), 27a, 39, 46a; and HT 100 and 11a, where the side is "unclear" or "partly" complete | +4 … +143 |
| **Running total:** HT 127b's second KU-RO (292) = its first KU-RO (156) + the five entries between them (136) | HT 127b (KU-RO 292) | +156 = the earlier KU-RO |
| **Sum too high: the scope rule catches entries that belong to another list or commodity** | HT 118 (−20), PH 31a (KU-RO + logogram + 1; −4), ZA 15b (+75, below a ruled-off heading), HT 123+124b (fractions, −523/60) | — |
| **Off by a fraction** | HT 13: 130 J against a sum of 131 (−1/2). HT 9a: 31 JE against a sum of 31 (+3/4, exactly the value of JE) | — |

### The value sets cannot be told apart by these totals
Corazza and Schrijver differ on B, D, K, H, A and the L series. **None of those signs occurs in any total whose arithmetic otherwise works.** The only total that involves them (HT 123+124b) mismatches under both sets. So on corpus-v0.1, **the totals constrain only J and E**, which both sets already value at 1/2 and 1/4. This is a useful negative for H-A2-01/02: on this corpus, the value-set comparison cannot be decided by totals.

### PO-TO-KU-RO
- **HT 122:** 31 + 65 = 96 against 97. A near miss (+1), on a damaged tablet; see H-A2-04.
- **HT 131b:** no KU-RO subtotals survive, so the scope is empty.

### KI-RO: 18 occurrences, 11 KI-RO/KU-RO pairs on the same side
Three candidate relations were tried on every pair. That makes 6 comparisons per pair, counting both value sets; all are counted here:
- a) KI-RO = the sum of the entries before it;
- b) KU-RO = all entries on the side − KI-RO;
- c) KU-RO = all entries on the side + KI-RO.

**None is exact in any pair, under either value set.** Under these naive scopes, KI-RO behaves neither as a subtotal nor as a simple additive or subtractive adjustment to the KU-RO. KI-RO rows have **not** been checked against GORILA (damage judged by the parser only), so this is weak.

## Leads worth keeping (each n = 1–3; test only on new data or with a pre-registered rule)
1. **Running totals.** A later KU-RO can include an earlier KU-RO (HT 127b). A scope rule "since the previous KU-RO, plus that KU-RO" could be registered and tested on corpus-v1.0 additions.
2. **Section and commodity scope.** HT 118, ZA 15b and PH 31a suggest that KU-RO totals one section or commodity, not the whole side.
3. **The two fraction offsets** (HT 13, −1/2; HT 9a, +3/4) are candidates for checking against GORILA readings and the literature (Montecchi 2009/2013).
4. **Damage standard.** Seven exact matches came from rows judged "damaged". The checking standard, or the reliance on restorations, needs revisiting before corpus-v1.0.
