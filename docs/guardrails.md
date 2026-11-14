# Guardrails for evaluating decipherment and pattern claims

Adopted by Marius on 2026-10-28, after the Ya Diktu null test (Finding 001). They apply to external papers and to anything Claude proposes.

1. **No match counts without a null.** Run the same pipeline against random pseudo-lexicons (same size and letter frequencies) and shuffled or random syllable strings. A match rate that does not beat the null is zero evidence.
2. **Run a known control.** Apply the method to Linear B words of known Greek meaning. If it "finds" the target language in Greek, the method is invalid.
3. **Count the degrees of freedom before judging readings.** Each of these widens the hit rate:
   - sign-value mergers (voicing, sibilants, r/l);
   - vowel-only signs read as a laryngeal, a morpheme or nothing;
   - unwritten weak radicals;
   - doubled signs;
   - affix menus;
   - the number of comparison languages pooled. In Finding 001, pooling more languages pushed random-lexicon matches from about 83% to about 94%.
4. **Red flag: orthography that changes word to word.** Examples: a sound written by different series in different words, or doubling that means different things in different places. Also: unattested morphology reconstructed to fit, and readings that rest on hapax words.
5. **Red flag: several incompatible decipherments of the same text.** If they exist in the same language family, or in different families, the method is under-constrained. Check prior readings before crediting a new one.
6. **Semantic fit is not a constraint.** "It makes sense for a prayer" is an added free choice, unless the meanings were pre-registered before looking.
7. **Correct data handling does not validate the inference.** Accurate corpus counts say nothing about whether the conclusions drawn from them hold.
8. **Apply all of these to Claude's own proposals too.**

The reusable null-test code from Finding 001 (swap the lexicon to test any "Linear A is X" claim) is in `src/aegean/benchmark/`; see `docs/benchmark.md`.
