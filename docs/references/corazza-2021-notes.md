# Notes on Corazza, Ferrara, Montecchi, Tamburini & Valério 2021

*The mathematical values of fraction signs in the Linear A script: A computational, statistical and typological approach.* Journal of Archaeological Science 125:105214. doi:10.1016/j.jas.2020.105214. Open access under CC BY-NC-ND 4.0. Copy: https://cris.unibo.it/retrieve/e1dcb336-9b0e-7715-e053-1705fe0a6cc9/Montecchi_JAS_125_2021.pdf

These are our own notes, read from the PDF on 2026-11-05. The PDF is not in the repo because its licence forbids derivatives. Page numbers refer to the journal pagination. Use these notes to find things in the paper, not as a substitute for it.

## What the paper does
1. **Sample:** Late Minoan I material only. MM II documents are excluded, and so are uncertain readings (L in KH 96, PH 7b, PH 12a, ZA 7b; MA 4a.1, CHIC #048) (pp. 1–2, n. 2).
2. **Six premises** (§2.1, pp. 3–4):
   1. J = 1/2, E = 1/4, F = 1/8.
   2. Combinations are additive.
   3. No value is written by two different signs, or by both a sign and a combination ("economical system").
   4. Any fraction sign or combination in a numeral phrase is < 1. The paper notes possible exceptions (J J, E E) in MM II material.
   5. **Any fraction is larger than the fraction to its right or below it.** The relations it lists from "unproblematic inscriptions" are J > E > F > K > L2 > L4; J > A; J > H; E > B; L(?) > L2. Footnote 3 gives the possible exceptions: E J on HT 123a.3–4 and ZA 8.4, against 28 cases of J E.
   6. The L series is divisive: L2 = L/2, L3 = L/3, and so on (hl = 1).
3. **Candidate values** (§2.4): 36 typologically motivated values from 5/6 down to 1/320. The L series may take any value from 1/2 to 1/320. W, X, Y and Ω are excluded.
4. **Constraint solving** in MiniZinc with the Gecode solver (§2.2):
   - Simulation 1 (L included): **2,172,836 solutions**.
   - Simulation 2 (L excluded): **3,794,740 solutions** (§3.1, §4.1).
   - L is dropped as an independent sign on frequency grounds (§3, Tables 4–5).
5. **Ranking** (§4.1):
   - G_FreqVSDiv = 1 − Spearman correlation between a sign's frequency and its number of common divisors;
   - G_AmbCombs = how many attested combinations would share a value;
   - G_Typ = how many values are typologically unattested.

   The product of these three (MULT) keeps the best 5,000 solutions. Those are then ranked by G_Optimal (incompleteness plus redundancy within the system's own fractional base). The best G_Optimal is **0.67094**, shared by two solutions.
6. **Result** (§4.2–4.4, Table 8): J 1/2, E 1/4, F 1/8, B 1/5, D 1/6, K 1/10, L2 1/20, L3 1/30, L4 1/40, L6 1/60; **H 1/16 (?), A 1/24 (?)**, which are tentative. Table 9 gives combination values, e.g. J E = 3/4, D D = 1/3, K L2 = 3/20, A A = 1/12 (?).
7. **Linear B link** (Table 10): D D, X (= A A?), K and the L shape resemble Linear B measure signs M (1/3), N (1/12), T (1/10) and V (1/60).

## Points that matter for A2
- **The values were not fitted to tablet totals.** The paper says (p. 2): "no Linear A inscription containing totals of numeral phrases is without reading or calculation problems (Montecchi, 2009, 2013)". HT 104 and PE 1 support J = 1/2, and HT Zd 156 is discussed. No list of totals used as constraints exists. So **H-A2-01 (do these values make the totals more consistent than random value sets?) is a new test**, and Montecchi 2009 and 2013 are the prior work on totals to read before registering it. Neither is in our hands yet; both appear to be paywalled (*AIIN* 55 and 59).
- **Descending order is premise 5.** Any test of ordering under these values is circular. H-A2-07's primary test is value-free for this reason.
- **Table 1** gives attestation counts of combinations from GORILA plus later publications. Examples: J E 24, D D 14, B B 5, E F 5, K L2 5, E L2 3, J B 3, J E L2 3, D D D D 1, plus single occurrences of 17 more. It is useful for cross-checking corpus-v0.1's counts. Note that lineara.xyz encodes J E and D D as the single Unicode ligatures A732 and A717.
- **Reproduction target for A2.3:** the solution counts of Simulations 1 and 2 under premises 1–6 and the stated value sets. The paper gives no code. Premise 4's "combinations in Table 1" and the exact form of the premise 3 constraints would have to be re-implemented from the text.
