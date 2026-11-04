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
