# H-A?-?? — short title

- **Logged:** YYYY-MM-DD (the merge commit is the timestamp of record)
- **Task:** A?.?
- **Layer:** L0 / L1 / L2
- **Type:** confirmatory / exploratory (CLAUDE.md rule 10: confirmatory = tested once on held-out data, chosen in advance; exploratory = training split, FDR-controlled. The corpus loader releases the held-out split only to a merged file whose line reads `- **Type:** confirmatory`.)
- **Status:** pre-registered

## Hypothesis
One falsifiable statement.

## Data
Corpus tag, inclusion rules, split (training / confirmatory / held-out).

## Test
Exact statistic and procedure, including tolerance rules and every free parameter, fixed now.

## Null model(s)
What would be expected if the hypothesis were false, and how it is generated (seeded).

## Known-script validation
Which known-answer run must pass first, and its pass criterion.

## Decision rule
What result counts as support, what counts as refutation, and what counts as inconclusive. Include the multiple-comparison correction and the size of the batch this belongs to.

**Power check (required):** the expected n, and the smallest p the test can attain at that n under the null. If it cannot go below the support threshold, the test cannot succeed: change the design or register it as descriptive. For permutation tests with n! ≤ ~10⁶, compute p by exact enumeration.

## What I already know that could bias this
Anything seen in advance (results, papers, held-out leaks).
