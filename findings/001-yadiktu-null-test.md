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

---

## Addendum 2026-11-04 — code restored, result reproduced, held-out check

**Code.** `experiments/finding-001/original/{nulltest,run,run2}.py` are the scripts from the 2026-10-28 session. They were restored verbatim from that chat's tool calls, including the two fixes applied during the session: the data path in `nulltest.py`, and the `cons` import in `run2.py`. `experiments/finding-001/reproduce.py` runs them unmodified against pinned inputs.

**Inputs.**
- lineara.xyz at commit `9c81beba…`, dated 2026-09-28. This was still `master` on 2026-11-02, so it is almost certainly the file fetched on 2026-10-28 (high confidence).
- HebrewStrong.xml at openscriptures commit `21c9add1…`, sha256 `a628f4f8…`.

**Reproduction.** Every figure in the Results table above was reproduced exactly:
- 0.800 (real Hebrew);
- 0.828 [0.805–0.851] (random lexicons);
- 0.734 (Linear B Greek words);
- 0.394 vs 0.424 for length ≥ 5;
- 0.908 and 0.935 for the 2× and 4× lexicons.

Real Hebrew (0.800) scores below all 20 random lexicons.

**Held-out exclusion.** Re-running with the sceptre records (`data/heldout.txt`) removed gives byte-identical output, still 696 sign-groups. Those records contributed no sign-groups to this test. This corrects research-notes 2026-11-04, item 3, which said they "probably" did.

**Two things the original write-up did not report:**
1. **Random syllable strings are beaten at longer lengths.** `run.py` also compares Linear A with random syllable strings (same lengths, same syllable frequencies). There, real sign-groups match more often than random strings at longer lengths: 0.475 vs 0.195 at length 5, 0.312 vs 0.021 at length 6, and 0.800 vs 0.747 overall. This does not change the conclusion. That null asks whether Linear A words differ from random strings, and they do: real words repeat affixes and follow phonotactic patterns, which the matcher's prefix and suffix menus exploit. The question Finding 001 asks is whether a *Hebrew* lexicon fits those same words better than random lexicons do, and it does not. Still, a full report should have shown this null, so it is recorded here.
2. **`run.py`'s Linear B figure is not the one to cite.** `run.py` reports 0.608 for the Linear B Greek control, while `run2.py` reports 0.734. `run.py` passes the words in lower case, so the upper-case prefix and suffix menus never match. 0.734 is the correct figure with affixes, and it is the one in the table.

**Status unchanged:** NEGATIVE for the Ya Diktu method. Confidence high.

---

## Addendum 2026-11-14 — the null was not size-matched; corrected under H-A5-01

**What was wrong.** The matcher lets a root's S be read as T, and D and T interchange. After that expansion the 502 Hebrew skeletons are 664 distinct forms. The random pseudo-lexicons of this finding also had 502 skeletons, but they expand to about 744, for two reasons: a random form has more S/D/T variants on average than a real root (1,064 variants against 1,014, summed over the 502 forms), and those variants coincide less often (320 lost to duplicates against 350). The first accounts for about 50 of the 80 extra forms, the second for about 30. The null therefore gave the matcher about 12% more targets than the real lexicon. Confidence: high (it is arithmetic on the lexicons; the sizes were rerun by the reviewers of H-A5-01, the two-part breakdown by the reviewer of this addendum, `docs/reviews/H-A5-01-outcome-review.md`).

**What that affects in the text above.**
- "Real Hebrew (0.800) scores below all 20 random lexicons" (addendum of 2026-11-04) and the table row "0.828 (0.805–0.851)" are correct as computed, but the gap came from the null's size, not from Hebrew. The same gap appears when the input is Greek: on 902 Linear B words of known Greek meaning, real Hebrew is 0.029 below this null.
- The comparison was tilted against the real lexicon. A small real advantage of Hebrew could have been hidden by it.

**Corrected test** (pre-registered as `hypotheses/H-A5-01.md`; outcome in `hypotheses/outcomes/H-A5-01.md`; corpus-v1.0 @ `ab8a6c9`, training split, layer L1). The null is 1,000 pseudo-lexicons with exactly 664 forms after expansion and the real lexicon's letter frequencies per position.

| Input | Real Hebrew | Size-matched pseudo-lexicons (95%) | Excess | p |
|---|---|---|---|---|
| Linear A, 414 sign-groups | 0.775 | 0.769 (0.734–0.800) | +0.006 | 0.397 |
| Linear B words of known Greek meaning, 902 | 0.532 | 0.512 (0.486–0.538) | +0.020 | 0.064 |
| the same, at Linear A's lengths | 0.684 | 0.660 | +0.024 | |

- Under a fair null Hebrew is neither below nor above random lexicons on Linear A: 396 of 1,000 random lexicons match at least as often.
- Hebrew's small edge over the size-matched pseudo-lexicons is larger on Greek words than on Linear A (difference −0.017, p = 0.840 for "larger on Linear A").

**Other differences from the original run.**
- **Inputs.** The original read lineara.xyz's `transliteratedWords` (696 sign-groups, all documents). That field is value-converted and is no longer parsed. The corrected test reads sign-groups from the corpus loader as L1 values, training split only, complete words only: 414 in the primary reading. Signs that L1 leaves as numbers (*56, *79) make a sign-group unreadable for the matcher; the original read them as PA3 and ZU.
- **Control.** The original 79 Linear B words were hand-entered in the session with no source. The corrected control is the 918-word Linear B–Greek list of Luo, Cao & Barzilay 2019 (DATA_SOURCES.md). The original statement "Greek fits it nearly as well" compared raw hit rates of inputs with different lengths; the corrected statement is the last row of the table and the difference test.
- The hit rates are lower than in the original (0.775 against 0.800) because the sign-group list differs. They are not comparable figure for figure.

**Status unchanged: NEGATIVE for the method.** The interpretation "a real Semitic lexicon fits Linear A no better than random consonant triplets" now rests on a fair null and a registered test. Confidence: high for this lexicon and this encoding of the licences.

**Limits, restated.**
- The encoding of the paper's licences is approximate, and the lexicon is Hebrew verbs only; the paper pools several languages, which raises the random match rate further (the lexicon-size sentence under the Results table; the size table in `experiments/A5.17/results/M1-hebrew-strong-verbs.md`).
- The test shows that this method cannot distinguish its lexicon from noise. It is not a test of whether Minoan is Semitic. On that question the literature survey (`docs/literature-survey-2026-10.md`, §6.5) records the Semitic proposals (Gordon, Best, di Mino 2026) as fringe, and "no match demonstrated with any family" as the consensus (Davis 2013; Salgarella 2025). This finding agrees with that consensus only in the narrow sense that one proposed demonstration fails.
- Everything is at L1: it assumes the Linear B values of the signs, as the paper does.
