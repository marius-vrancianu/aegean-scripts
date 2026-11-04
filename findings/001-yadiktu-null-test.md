# Finding 001 — Null-model test of di Mino (2026) "Ya Diktu" root-matching method
Date: 2026-10-28. Status: NEGATIVE for the paper's method (method cannot discriminate Semitic from noise).

> Repo note (2026-11-04): moved in from the claude.ai project. The code (`nulltest.py`, `run.py`, `run2.py`) is not yet in the repo, and the lineara.xyz commit used was not recorded. The source file is now known to contain the held-out sceptre records (research-notes 2026-11-04). Re-run with the exclusion once the code is in. The conclusion is not expected to change.

## Data
- Linear A: lineara.xyz (mwenge/lineara.xyz, LinearAInscriptions.js, master, fetched 2026-10-28; GORILA-derived; transliteration in Linear B homomorph values). 696 unique sign-groups of >=2 syllabograms (*301 read as NA per the paper).
- Hebrew: openscriptures HebrewLexicon, HebrewStrong.xml (CC BY 4.0). Verb lemmas only -> 502 consonantal skeletons.
- Control: 79 Linear B words of known Greek meaning (hand-entered).

## Machine (encodes the paper's own licences)
- Mergers: stop, sibilant and liquid mergers; S~T for emphatic s (the paper's claim); D~T.
- Pure-vowel signs count as a laryngeal or as nothing.
- One unwritten weak radical (', w, y) is allowed.
- Doubled signs collapse.
- Prefix menu: A, TA, JA, I, U-NA, NA, WA, RA, A-TA, TA-NA, JA-TA, A-NA.
- Suffix menu: ME, MA, TU, TI, TE, NU, JA, SE, I, KA, NA, NE, TI-NU, U-TI-NU, MI-NA, TE-TE.
- Sanity check: the machine reproduces a root for all 7 IO Za 2 words.

## Results
| Input | Lexicon | Hit rate |
|---|---|---|
| Linear A | real Hebrew verbs | 0.800 |
| Linear A | 20 random pseudo-lexicons, same size & letter freq | 0.828 (0.805-0.851) |
| Linear B Greek words | real Hebrew verbs | 0.734 |
| Linear A len>=5 | real Hebrew | 0.394 ; random lexicon 0.424 |

Lexicon size: doubling the random lexicon raises the Linear A hit rate to 0.908, and quadrupling it to 0.935. The paper pools about 8 languages.

## Interpretation
- A real Semitic lexicon fits Linear A no better than random consonant triplets, and Greek fits it nearly as well. Root matching under these licences carries no evidential weight.
- Semantic "fit" is an additional free choice, not a constraint, unless it is pre-registered.
- The corpus figures in the paper check out: *301 occurs 238 times standalone out of about 287–291 occurrences, and a/i/u make up 80.5% of vowels against the paper's 80.8%. The data handling is fine; the inference is not.

## Limitations
- The lexicon is Hebrew verbs only, which is conservative.
- The affix menus are approximate.
- No semantic filter was modelled.
