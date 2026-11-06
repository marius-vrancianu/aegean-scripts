# Independent review — Finding 002 (A2 arithmetic, corpus-v0.1)

- **Reviewer:** a separate Claude instance (claude.ai session, 2026-11-06) that did not produce Finding 002 or any A2 code. Required by `CLAUDE.md` § Workflow.
- **Reviewed:** `findings/002-a2-arithmetic-corpus-v0.1.md` at `main @ 73582be`, plus H-A2-04/07/08 and their outcomes, `experiments/A2/exploratory/`, `docs/references/corazza-2021-notes.md`.
- **Reproduced:** corpus-v0.1 rebuilt (sha256 `bb14ce5c…` matches); `run_h_a2_07.py` rerun with identical output. Extra checks below were run on the same corpus.
- **Primary source checked:** Corazza et al. 2021 (PDF), pp. 2–4 and n. 3.
- **Not read (blinding respected):** *Anetaki II*, Kanta et al. 2025, Kanta–Perna, KN Zg 57/58.
- **Not checked:** GORILA facsimiles, Younger's apparatus, Montecchi 2009/2013.

## Verdict
**Accept after corrections.** The two load-bearing results stand: fraction signs follow a fixed order in this transcription (H-A2-07), and where totals can be computed they add up far above chance (exploratory census). Three statements are wrong and must be corrected before the finding is cited: the H-A2-08 decision label, the claim that the arithmetic supports J = ½, and "no pair ever appears in both orders".

## Major issues

### M1. H-A2-08 is "not supported" by its own frozen rule, not "inconclusive" — and the test could never have said "supported"
*Confidence: high (exact enumeration).*

- The five testable rows have sums (10, 6, 159, 50, 3) and totals (10, 6, 160, 30, 78). Only two totals can match any sum, so ≥ 2 exact matches happens in exactly 3! of 5! = 6/120 permutations. **Exact p = 0.0500.**
- The reported p = 0.0493 is Monte Carlo noise (SE ≈ 0.0022 at 10,000 permutations). The frozen rule says "not supported: p ≥ 0.05", so the correct label is **not supported**.
- **Power:** with 5 rows of distinct totals, the smallest attainable p is 1/120 = 0.008 (all 5 exact). Three exact matches give p ≥ 2/120 = 0.017. "Supported" (p < 0.01) therefore required a perfect 5/5. This was knowable before the run.
- **Correct reading:** not supported by the frozen rule, because the test had essentially no power. It is uninformative about KU-RO, and in particular it is **not** evidence that KU-RO is not a total. The outcome file's prose already says roughly this; only the label and the "between the thresholds" wording are wrong.
- **Fix:**
  - correct `hypotheses/outcomes/H-A2-08.md` (mutable) and Finding 002 summary item 2;
  - add a research-notes correction entry;
  - for permutation tests on small n, compute p exactly by enumeration when n! ≤ ~10⁶;
  - add a line to `hypotheses/TEMPLATE.md`: "minimum attainable p under the null, given the expected n — must be below the support threshold."

### M2. "The arithmetic supports J = ½" is circular
*Confidence: high (Corazza 2021 p. 2; census rows checked).*

- Corazza et al. (p. 2, following Bennett 1980) **deduce** J = ½ from HT 104: 45 + J + 20 J + 29 = 95. HT 104 is also the only exact total in the census that contains a fraction sign. Using it to "support" J = ½ counts the source of the value as evidence for it.
- The only other fraction-bearing KU-RO totals are mismatches: HT 13 (−½) and HT 9a (+¾). **No exact total contains E.**
- **Fix:**
  - "What this means": delete "and of J = ½". Say instead that the totals reproduce HT 104 under J = ½ and give no independent evidence for any fraction value.
  - Negative result: replace "totals constrain only J and E" with "the only working total with a fraction sign is HT 104, the text J = ½ was derived from; no working total contains E or any sign on which the value sets differ".

### M3. "No pair of fraction signs ever appears in both orders" is false as written, and the regularity is not new
*Confidence: high for the counterexample, medium for the encoding explanation.*

- Corazza et al. n. 3 list 28 cases of J E against two doubtful E J (HT 123a.3–4, ZA 8.4). Corpus-v0.1 contains ZA 8's "E J". Lineara.xyz encodes J E as the single ligature codepoint JE (31 occurrences), which H-A2-07 excluded from pair counts by its pre-registered design.
- The headline claim therefore holds only because the 31 J-before-E cases are hidden inside a codepoint.
- **Sensitivity (exploratory, not a re-test):** splitting JE → J, E and DD → D, D gives 72 pairs. The result is C = 0.986 (one E→J against 31 J→E), still acyclic, permutation p < 0.0001 (null mean 0.65). The result survives and gets stronger.
- **Fix:**
  - Reword the claim to: "Apart from one E J (ZA 8, also flagged as doubtful by Corazza n. 3), no pair of separately encoded fraction signs appears in both orders."
  - State that the fixed descending order is Bennett's observation and Corazza's premise 5. H-A2-07 is a formal, value-free null test that replicates it on one transcription; it is not a new discovery.

## Minor issues
- **m1. Site clustering.** E→F (5/5) is all Hagia Triada; K→L2 (5/5) is all Khania, three of them from KH 11.
  - Counting each pair at most once per document leaves C = 1.00 over 39 pairs, so pseudoreplication does not drive the result.
  - However, cross-site agreement rests only on J→B, E→L2, J→L2 and JE→L2.
  - The sceptre is from Knossos, so H-A2-06 assumes the order transfers across sites. Say so in the finding.
- **m2. Linearisation.** Corazza note larger fractions are written "to the left or above". Stacked signs are put in linear order by the editors.
  - If GORILA or lineara linearise by convention, H-A2-07 partly measures editorial practice.
  - Add a sample of stacked combinations to `docs/manual-checks/A2-checklist.md`. Confidence that this is a real problem: low; that it is unchecked: high.
- **m3. KI-RO overstated.** "None of three relations holds in any of 11 pairs" is too strong. Relation (a) was evaluable on 4 pairs, and (b)/(c) on 7. The rest were unvalued or had an empty scope. Give those denominators.
- **m4. "The edition itself marks."** This is lineara.xyz's damage marking, not GORILA's apparatus. Name the source.
- **m5. Exploratory p-values.** Flag the p < 0.0001 in summary item 3 as uncorrected and post hoc. It was run after H-A2-08 failed, under two scopes and two value sets (Rule 2).
- **m6. Rosters.** Three of the 9 exact matches (HT 117a, HT 88, HT 94b), including both clean ones, are lists of 1s whose total is the entry count. They confirm KU-RO = total but are the weakest arithmetic. Note it.

## Robustness checks that support the finding
*Exploratory, run by the reviewer.*

| Check | Result |
|---|---|
| H-A2-07 rerun | Identical to committed JSON |
| H-A2-07, one count per pair per document | 39 pairs, C = 1.00 |
| Census, null stratified by magnitude of the sum (1–9 / 10–99 / ≥ 100) | null mean 1.33 exact vs 9 observed; p < 5 × 10⁻⁵ (20,000 permutations) |
| Census without the three rosters, HT 104 (circular) and HT 85a (restored total) | 4 of 24 exact (HT 11b, HT 25b, HT 89, HT 9b); null mean 0.25; p ≈ 10⁻⁴ |

The "totals behave like totals" conclusion survives a stricter null and the removal of every case open to circularity.

## Requested changes (one hand-merge PR)
1. Correct the H-A2-08 label and wording (M1), in the outcome file and Finding 002 item 2. Add the minimum-attainable-p line to the template.
2. Remove the J = ½ support claim and rewrite the negative result (M2).
3. Reword the "both orders" claim and credit Bennett / Corazza premise 5 (M3).
4. m1–m6 as wording changes; add m2 to the manual checklist.
5. Add a research-notes entry recording this review and the corrections, linking this file.
