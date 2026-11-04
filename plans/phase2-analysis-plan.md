# Phase 2 Analysis Plan & To-Do (derived from Literature Survey §9)

Version 1.2 — updated 2026-11-04 (v1 created 2026-10-31; v1.1 2026-11-02). Supersedes §9 of the Phase 1 literature survey as the working plan. The survey itself remains a dated snapshot (status as of October 2026).

How to use this file:
- Each analysis has an ID (A1–A7). Tasks are numbered A<n>.<m>. Use these IDs in the hypothesis log, commit messages and findings files.
- Hypotheses get IDs of the form H-A<n>-<nn> and are logged *before* the test is run (Rule 3), as one file each in `hypotheses/` (see `hypotheses/README.md`).
- Status markers: `[ ]` open, `[~]` in progress, `[x]` done, `[-]` dropped (with reason in the change log).
- When a task produces a result (positive or negative), write `findings/NNN-<slug>.md` and link it here.

---

## 0. Cross-cutting rules and decisions

### 0.1 Three data layers (never mix them silently)
| Layer | Content | Status of the content |
|---|---|---|
| **L0 — signs** | GORILA/Bennett sign IDs (AB nn, A nnn), sign roles, numerals, fractions, damage flags, document metadata | Closest to the evidence. Ground truth. |
| **L1 — conventional transliteration** | Linear B homomorph values (KU-RO, *301 kept as *301) | Mainstream assumption (homomorphy–homophony), not proven. |
| **L2 — phonological hypothesis** | Per-sign phonological feature distributions + learned spelling channel + per-word lattices of possible underlying forms | Explicit, versioned hypothesis. Logged like any other claim. |

Every result states which layer it was computed on. Internal analyses (A2, A3, A4, A7) run on L0 and are interpreted with L1 afterwards. Only cross-language comparison and typology (A5, A6) use L2.

### 0.2 Decision D1 (2026-10-31): no text-to-speech / audio representation
Converting the corpus to synthetic audio and analysing acoustics was considered and rejected.
- TTS output is a deterministic function of the transliteration plus the engine's built-in phonology. It cannot add information; it can only add artefacts (vowel qualities, stress, allophony, timing of whatever language the TTS voice was built for).
- Acoustic similarity would then measure the TTS language, not Minoan, and would make the transliteration look more certain than it is.
- The legitimate concern behind the idea (comparing *spellings* across scripts is not comparing *languages*) is addressed instead by the symbolic L2 layer (A5.P, A5.C).

### 0.3 Decision D2 (2026-10-31): the spelling channel is learned from data, not hand-coded
The rules for how sounds become Linear-script spellings (omitted final consonants, l/r merger, voicing/aspiration not written, cluster handling) are estimated as probabilities from the Linear B corpus and its known Greek readings (A5.C), instead of being written by hand. Three caveats are permanent and must be carried into every result that uses the channel:
1. **Circularity.** Greek readings were accepted partly because they fit the known spelling rules; unreadable words dropped out. The learned channel will look cleaner than reality.
2. **Reconstructed target.** The Greek side is reconstructed Mycenaean (labiovelars, digamma, h-), derived from alphabetic Greek plus comparative Indo-European.
3. **Transfer.** Linear B rules describe *Greek squeezed into a script built for Minoan*. Minoan in its native script may have needed fewer, or different, omissions. The Linear B channel is one hypothesis about the Linear A channel, not a measurement of it. The transfer gap is measured, not assumed (A5.C tests T1–T3).

### 0.4 Statistical protocol
- **Null first.** Every pattern is tested against an explicit null before it counts (Rule 1).
- **Validate on a known script first.** Every method is run on Linear B (and, where relevant, on Cypriot or Ugaritic) before Linear A (Rule 4).
- **Multiple comparisons.** Count every hypothesis tested in each analysis; control false discovery rate (Benjamini–Hochberg) for exploratory batches; report the full count, including failures (Rule 2).
- **Held-out data policy** (fixed at the A1 v1.0 release, never changed afterwards):
  - KN Zg 57 and KN Zg 58 (Knossos ivory sceptre) are reserved as held-out until predictions from A2–A4 are frozen. Blinding was partly compromised on 2026-11-02; see `research-notes.md` for what was seen and its consequences.
  - A random 20% of documents, stratified by site and support type, is frozen as a confirmatory split for A3 and A4.
- **Blinded checks** (added 2026-11-02): a web fetch is not a blinding mechanism. Any check on held-out material is done either by a separate agent that returns only pre-specified fields, or by Marius after predictions are frozen.
- **LLM output is a hypothesis, never evidence** (Rule 5). This applies to any sign value, segmentation or reading Claude suggests while working on these tasks.

### 0.5 Dependencies and suggested order
```
A1 (corpus) ──┬──> A2 (arithmetic)
              ├──> A3 (affixes)
              ├──> A4 (sign values) ──> held-out test on sceptre
              ├──> A5 (power analysis) <── A5.C (spelling channel; Linear B data only, can start now)
              │                                │
              │                                └──> A6 (typology)
              └──> A7 (script relations; independent, lowest priority)
```
- A5.C can start in parallel with A1 because it only needs Linear B data.
- Phase gate: no "which language family?" test (Phase 3) until A5 shows that some method has measurable power at Linear A's scale.

---

## A1 — Canonical, versioned Linear A corpus

**Goal.** One canonical, documented, versioned corpus that every later analysis uses, with explicit inclusion rules and provenance.

**Why.** Published document counts disagree (1,427 in the Linear A Digital Corpus; 1,534 per RILA Suppl. 1 as cited by Navarre-AI; 772–787 in SigLA harvests). Without a fixed list, no result is reproducible.

**Sources.** SigLA (preferred machine-readable source), lineara.xyz (already used in Finding 001), Younger's transliterations, GORILA sigla as universal keys. Control corpus: DAMOS (Linear B).

**Deliverables.** `data/` with raw snapshots + processed corpus; `docs/schema.md`; `DATA_SOURCES.md` (source, version/date, licence, conventions); tagged release v1.0; baseline statistics report.

To-do:
- [x] A1.1 Set up the GitHub repo structure (https://github.com/marius-vrancianu/aegean-scripts): `data/raw`, `data/processed`, `src/`, `notebooks/`, `findings/`, `hypotheses/`, `research-notes.md`, `DATA_SOURCES.md`, `CLAUDE.md`, CI guardrails. Done 2026-11-04, including the Finding 001 code (`experiments/finding-001/`, reproduced exactly).
- [ ] A1.2 Verify the SigLA licence directly on the site (survey reports CC BY-NC-SA 4.0 secondhand). Record exact terms and what redistribution is allowed.
- [~] A1.3 Establish the lineara.xyz licence. 2026-11-04: the repo has no LICENSE file (all rights reserved by default), so we fetch rather than commit. Still to do: ask the maintainer. Record it for Finding 001's data provenance too.
- [ ] A1.4 Harvest SigLA: documents, sign tokens, sign roles (syllabogram/logogram/numeral/fraction/ligature), word division, findspot/support metadata. Store a dated raw snapshot with a content hash.
- [~] A1.5 Snapshot lineara.xyz (`LinearAInscriptions.js`, commit hash) and Younger's transliteration pages (date of access). lineara.xyz pinned 2026-11-04 (`data/raw/lineara.xyz/fetch.py`); Younger still to do. **The snapshot contains the sceptre records; see `data/heldout.txt` and research-notes 2026-11-04.**
- [x] A1.0 (added 2026-11-04) Provisional single-source release **corpus-v0.1**: lineara.xyz only, L0, held-out excluded; built by `python -m aegean.corpus.build`, hashes in `data/processed/corpus-v0.1/MANIFEST.json`. For A2 until corpus-v1.0; every A2 result on it carries the single-source caveat and is re-run on v1.0.
- [ ] A1.6 Reconcile the document lists. Write explicit inclusion rules (support type, minimum legibility, site, period, register) and produce one canonical list keyed by GORILA siglum.
- [ ] A1.7 Define the schema: document → line (where known) → sign-group → sign token. Fields per token: GORILA sign ID, role, damage/uncertainty flag, alternative readings with their source. Fields per document: site, support, period (LM IB etc.), register (administrative / religious / other), scribal hand where published.
- [ ] A1.8 Build layers L0 and L1 (L2 comes from A5).
- [ ] A1.9 Cross-source disagreement report: list every place where SigLA, Younger and lineara.xyz differ. This is a data-quality result in its own right.
- [ ] A1.10 Linear B control corpus: check whether DAMOS offers raw data download (its developers have said they plan to release raw data); otherwise request it or harvest the online version within its terms. Keep its lemma/normalisation layers.
- [ ] A1.11 Baseline statistics: sign frequencies, positional statistics (initial/medial/final), sign-group length distribution, breakdown by site/period/register. Re-derive Packard-style figures as a sanity check.
- [ ] A1.12 Freeze the held-out split (§0.4), then tag release v1.0 with a changelog.
- [ ] A1.13 When a readable edition text of KN Zg 57/58 is available (the 2025 *Ariadne* overview has no sign-by-sign transcription; wait for *Anetaki II*), add it under the held-out flag.

---

## A2 — Accounting-constraint analysis (KU-RO / KI-RO / PO-TO-KU-RO, fractions)

**Goal.** Formalise every Linear A list with a total, a deficit or a grand total as an arithmetic constraint system, and use it to test fraction values and the meaning of KI-RO. The ground truth is arithmetic, so the results do not depend on knowing the language.

**Inputs.** A1 L0 with numerals and fraction signs parsed into terms.

**Method.** Parse each list into entries and totals. Represent integer and fraction terms exactly (rational arithmetic). Search over candidate fraction-value assignments (unit fractions 1/2 … 1/60 and additive combinations) with a constraint solver (e.g. z3 or OR-Tools) or exhaustive search, scoring how many totals each assignment makes consistent, with an explicit tolerance model for damaged entries and scribal error.

**Validation on a known script.** Run the same checker on Linear B lists with *to-so* totals (DAMOS) and confirm it reports sensible consistency rates. Reproduce Corazza et al. 2021's reported results with their value set before testing anything new.

**Null models.** (i) Random value sets drawn from the same candidate space → distribution of consistency scores; (ii) numbers shuffled across entries within a document; (iii) chance rate at which a random number in the total slot would match.

**Initial hypotheses (to log before testing).**
- H-A2-01: The Corazza et al. 2021 value set (J=1/2, E=1/4, B=1/5, D=1/6, F=1/8, K=1/10 …) gives significantly more consistent totals than random value sets.
- H-A2-02: It also outperforms the published alternative value sets (compile the list: Bennett 1950, Facchetti, Schrijver, others).
- H-A2-03: KI-RO entries behave arithmetically like deficits. Pre-register the exact candidate relations (e.g. total = sum of entries; total = sum − KI-RO; KI-RO = expected − received) before looking at the results.
- H-A2-04: On HT 122, PO-TO-KU-RO equals the sum of the KU-RO subtotals (sanity check).
- H-A2-05 (exploratory): constraints narrow the values of the low-frequency signs (H, A, L-series, W, X, Y, Ω).
- H-A2-06 and H-A2-07: sceptre fraction-order test, see A2.9.

To-do:
- [x] A2.1 Write the parser for numerals and fraction sequences; unit-test it on hand-checked tablets (e.g. HT 104: 45 + J + 20 J + 29 = 95 per Corazza et al.). Done 2026-11-04: `aegean.arithmetic.parse`; fractions kept symbolic; fixtures HT 104, HT 13, HT 122a checked against GORILA facsimiles (`tests/test_arithmetic_parse.py`). On corpus-v0.1: 1,566 entries, 434 flagged damaged, 202 with no label on their line.
- [~] A2.2 List every document with KU-RO, KI-RO or PO-TO-KU-RO; classify each as complete / damaged / indeterminate. 2026-11-04: rule-based inventory on corpus-v0.1 (`experiments/A2/inventory-corpus-v0.1.csv`, rules in `inventory-rules.md`): 55 marker occurrences in 42 documents; 9 complete, 7 complete-scope-unclear. **Still to do:** check each candidate row against the GORILA facsimile, because the source's damage flags are incomplete.
- [ ] A2.3 Reproduce Corazza et al. 2021. **Revised 2026-11-04 (V7):** their values were not fitted to tablet totals. They come from six premises solved in MiniZinc/Gecode (2,172,836 / 3,794,740 solutions), then ranked by frequency, typology and optimality, with HT 104 and PE 1 cited only as support. So: (a) the reproduction target is their solution counts and final ranking under their premises (needs the premises verified from the PDF); (b) H-A2-01, whether their value set makes tablet totals more consistent than random value sets do, is a **new** test, not a reproduction.
- [ ] A2.4 Build the Linear B *to-so* validation set and run the checker. Source route (V3): DAMOS word-search CSV for *to-so* plus the online texts of those tablets (CC BY-NC-SA 4.0), or a data extract requested from the editor.
- [ ] A2.5 Log H-A2-01…05 with exact test definitions and tolerance rules.
- [ ] A2.6 Run the value-set comparison and the null distributions.
- [ ] A2.7 Run the KI-RO relation test.
- [ ] A2.8 Write up: a table of every total (consistent / inconsistent / indeterminate) under each value set, plus the null comparison.
- [ ] A2.9 (revised 2026-11-02) **Sceptre fraction-order test (held-out).** KN Zg 57 has no numerals. KN Zg 58 face δ has vases, units and six distinct fraction signs in sequence, and no total word is reported (Kanta et al. 2025, pp. 40–42). The original total-consistency test is therefore impossible. Replacement test:
  - **H-A2-07 (run first, on the training corpus):** in Linear A entries with two or more different fraction signs, the signs are written in descending order of value under the A2 value set. Report the rate and its exceptions. If the rate is not close to 1, drop H-A2-06 as untestable and record why.
  - **H-A2-06 (held-out):** under the frozen A2 value set, the six fraction signs on KN Zg 58 δ occur in strictly descending order.
  - **Null:** a random ordering of six distinct values is descending with probability 1/720. For the real null, sample value sets from the A2 candidate space and compute the share that make the observed sequence descending.
  - **Preconditions:** (1) H-A2-07 passes; (2) sign identities and order are taken from *Anetaki II* (Kanta ed., forthcoming); (3) A2 predictions are frozen and hashed before reading that edition.
  - **Blinding status:** partly compromised. See `research-notes.md`, 2026-11-02. A positive result is confirmatory only for value sets that differ from Corazza et al. 2021 on these signs.

---

## A3 — Affix discovery against null models

**Goal.** Test, with explicit nulls and a known-answer control, whether the prefixes and suffixes proposed by hand (Duhoux, Davis, Thomas, Salgarella) are statistically real, and discover others.

**Layer.** L0 (sign IDs). Interpretation in L1 only afterwards, so a result like "-JA is productive" does not depend on the Linear B values being right.

**Methods.** Two segmenters at most, plus a simple statistic: Morfessor Baseline (MDL), a Bayesian segmenter (Dirichlet-process unigram/bigram type), and Harris-style successor/predecessor variety counts.

**Validation on a known script.** Run the identical pipeline on Linear B at the sign-ID level. Measure precision and recall against a gold list of Mycenaean inflectional endings compiled from a standard grammar and frozen before running. Repeat after subsampling Linear B to Linear A's token count to measure the method's power at that size.

**Null models.**
- (a) Signs permuted within each sign-group (length and unigram frequencies preserved).
- (b) Bigram-preserving Markov corpus. This is the critical null: it shows how much "affix-like" structure arises from phonotactics alone.
- (c) Site-stratified runs, to check whether an affix is just a Hagia Triada scribal convention.
- (d) Context-stratified runs (list headwords vs libation formula vs other), because list entries are mostly personal names and suffixes may be name-formation.

**Initial hypotheses.** H-A3-01 J-/JA- prefix; H-A3-02 A- prefix (A-SA-SA-RA-ME ~ JA-SA-SA-RA-ME); H-A3-03 -JA suffix; H-A3-04 -RU; H-A3-05 -RE; H-A3-06 TA-NA- prefix (Thomas 2020). Any further candidates are extracted from the literature and logged before the run; everything discovered beyond these is exploratory and FDR-controlled.

To-do:
- [ ] A3.1 Compile the candidate affix list with sources (Duhoux, Davis 2013/2014, Thomas 2020, Salgarella 2025 via secondary summaries).
- [ ] A3.2 Compile and freeze the Linear B gold list of endings.
- [ ] A3.3 Implement the null corpus generators (a)–(d).
- [ ] A3.4 Validate on Linear B (full and subsampled to Linear A size). If the method cannot recover Greek endings at Linear A's size, record that as a negative result and stop before Linear A.
- [ ] A3.5 Log H-A3-01…06 and the exploratory protocol.
- [ ] A3.6 Run on the Linear A training split; then confirm on the frozen 20% split.
- [ ] A3.7 Write up: affix inventory with effect sizes, q-values, site/context stratification and Linear B power figures.

---

## A4 — Distributional sign-value testing

**Goal.** (a) Test the homomorphy–homophony principle quantitatively; (b) place undetermined signs (*301, *118 etc.) by distribution and make predictions that can be checked on held-out text.

**Methods.**
- **Alternation test (Kober-style).** Find pairs of near-identical sign-groups that differ by one sign. Under Linear B values, do the swapped signs share a consonant or a vowel more often than chance? Null: random permutations of the value grid.
- **Grid recovery.** Cluster signs by context (neighbour and position profiles). Validate on Linear B with values masked: does clustering recover consonant series and vowel columns (the Kober/Ventris grid) above chance? Then apply to Linear A.
- **Undetermined signs.** Locate *301 and other A-only signs within the recovered grid. Note that Finding 001 encoded di Mino's *301 = NA; whether *301 patterns with the n-series is a clean, testable claim.
- **Shared names.** Use Linear A–Linear B shared names as a fixed check on values.

**Null models.** Value-grid permutations; shuffled contexts; Linear B with masked values as the known-answer control.

**Initial hypotheses.** H-A4-01: alternating signs share consonant or vowel (under Linear B values) more than under permuted grids. H-A4-02: grid clustering on Linear B recovers series/columns above chance at Linear A's corpus size. H-A4-03…: one pre-registered prediction per undetermined sign (series and/or vowel), frozen before the held-out test.

To-do:
- [ ] A4.1 Implement the alternation-pair extractor and the grid-permutation null.
- [ ] A4.2 Validate grid recovery on Linear B (full and at Linear A size).
- [ ] A4.3 Run H-A4-01 on Linear A.
- [ ] A4.4 Run grid recovery on Linear A; place undetermined signs.
- [ ] A4.5 Freeze predictions for *301, *118 and the other undetermined signs in the hypothesis log.
- [ ] A4.6 Test predictions on the frozen 20% split and on KN Zg 57/58. Note: the sceptre is a cult-building, inventory-like text by two hands; a miss there may reflect register or hand, and the write-up must test for that before treating it as falsification.
- [ ] A4.7 Write up, including signs where the Linear B value does *not* behave as expected.

---

## A5 — Decipherability power analysis (benchmark)

**Goal.** Measure whether *any* language-matching method can (i) identify the correct related language above random and unrelated-language baselines and (ii) recover correct cognates, once known language pairs are degraded to Linear A's conditions. Output: success curves as a function of corpus size, spelling-channel noise, sign-value noise and lattice permissiveness, plus an open benchmark repository.

**Why it matters.** It generalises Finding 001 (real Hebrew vs random lexicons) into a quantitative standard. If no method succeeds at Linear A's scale, that is a publishable negative result, and future claims (di Mino, Revesz, Gordon-style) can be judged against it. If some method does succeed, it defines the only legitimate design for a Phase 3 family test.

### A5.1 Known-answer pairs
- Linear B → Greek: Luo, Cao & Barzilay 2019 dataset, 919 cleaned pairs plus a 455-pair names-only subset (NeuroDecipher GitHub repo, with the preparation notebook).
- Ugaritic → Hebrew: same repo (Snyder et al. 2010 data).
- Gothic / Iberian: Luo et al. 2021; data and code availability to be checked.
- Negative controls: pairs that should not match (e.g. Linear B vs Hebrew, Ugaritic vs Greek).

### A5.2 Degradation to Linear A conditions
- Token budget about 7,400 signs; unique multi-sign-group inventory matched to Linear A (about 700 in lineara.xyz per Finding 001; recompute from A1).
- Share of personal names and place names matched to Linear A list contexts.
- Defective spelling applied through the learned spelling channel (A5.C), not ad hoc rules.
- Sign-value noise: 10–14% of signs perturbed (Packard / Duhoux / Owens orders of magnitude).
- Fragmentation: damaged-sign rate taken from A1 statistics.

### A5.3 Methods under test
- M1: the Finding 001 root matcher (Ya Diktu licences).
- M2: sound-class edit-distance matching (LingPy SCA / Dolgopolsky classes).
- M3: NeuroDecipher (Luo et al. 2019).
- M4: Luo et al. 2021 phonetic-prior language-closeness measure, if the code is available.
- M5: a simple probabilistic alignment baseline.

### A5.4 Baselines and metrics
- Baselines: random lexicons matched in size and phoneme/letter frequency (as in Finding 001); real but unrelated languages; shuffled target lexicons.
- Metrics: rank of the true relative among K candidate lexicons; AUC against random lexicons; cognate precision@k; calibration of match scores.

### A5.P Phonological hypothesis layer (L2)
Background: decision D1 (no audio) and the 2026-10-31 discussion. Comparing Linear B-value strings with, say, Hebrew consonant roots compares two writing conventions, not two languages. The fix is a symbolic representation of possible sounds.
- **Per-sign feature distributions.** Each syllabogram maps to a weighted set of phonological feature bundles (place, manner, voicing, vowel height), using PanPhon feature vectors for IPA symbols, with sound classes (LingPy SCA / Dolgopolsky) as a coarser variant. Value uncertainty is explicit: e.g. the r-series covers /r/ and /l/; the d-series may have been a fricative; the z-series is uncertain.
- **Lattice expansion.** Each sign-group becomes a weighted lattice of possible underlying forms, produced by composing the feature distributions with the spelling channel from A5.C.
- **The trap.** Every expansion adds possible readings and therefore cheap matches. This is the Ya Diktu failure mode seen in Finding 001. Therefore:
  - The lattice (channel version, weights, pruning threshold) is frozen and hashed before any comparison.
  - All null lexicons and controls go through exactly the same lattice.
  - Results are reported as a **permissiveness curve**: hit rate for the true relative and for nulls as a function of lattice size. A method only "works" if the gap persists at realistic permissiveness.

### A5.C Spelling-channel sub-project (learned from Linear B; decision D2)
**Model.** P(spelling | underlying form): a weighted finite-state transducer or EM-trained alignment model from (reconstructed) Mycenaean phonological forms to Linear B sign sequences. It should run on a single PC.

**Parameters to estimate** (examples, not an exhaustive list): probability of omitting final -s, -n, -r; l → r-series; voicing and aspiration neutralisation (except d); cluster handling (first consonant dropped vs dummy vowel copied from the next syllable); omission of initial s- before a stop; diphthong and glide handling.

**Training data.** Luo et al. 2019 pairs; DAMOS lemmas; the jhnwnstd/shannon lexicon (MIT, 2,272 entries, reportedly based on Chadwick & Ventris; quality unverified). Greek forms must be converted to a phonemic Mycenaean representation; document every conversion rule.

**Validation.** k-fold held-out prediction of Linear B spellings from Greek forms.

**Caveat handling** (from D2):
- C1 circularity: train two versions — all accepted pairs, and a *secure* subset (toponyms with alphabetic continuations; words confirmed by an adjacent logogram). Report how much the parameters shift.
- C2 reconstructed Greek: document the reconstruction choices; run a sensitivity check where feasible.
- C3 transfer: measured by tests T1–T3 below.

**Transfer-gap tests.**
- **T1 — Cypriot syllabary.** The same language (Greek) in a different syllabary with different conventions: final consonants written with a dummy -e vowel sign, clusters written out. Train the channel on Linear B, test on Cypriot. The size of the failure measures how much the rules depend on script convention rather than on language. Requires an open digital Cypriot syllabary corpus (not yet identified).
- **T2 — Pre-Greek Cretan toponyms.** Linear B spellings of non-Greek place names against their later alphabetic forms (ko-no-so/Knossos, a-mi-ni-so/Amnisos, tu-ri-so/Tylissos, pa-i-to/Phaistos, ku-do-ni-ja/Kydonia, ru-ki-to/Lyktos; compile and verify a complete list). Fit the channel on this subset and compare it with the Greek-vocabulary channel. A significant difference would itself be a finding about Minoan sound structure. Caveats: the alphabetic forms are Greek adaptations; the sample is small, so use bootstrap confidence intervals.
- **T3 — Direct Linear A ↔ Linear B pairs** (QA-QA-RU/qa-qa-ro, DI-DE-RU/di-de-ro, PA-I-TO/pa-i-to, SU-KI-RI-TA/su-ki-ri-ta, SE-TO-I-JA/se-to-i-ja …). Too few to estimate parameters; used only as a consistency check on the other channels.

**Output.** Versioned, hashed channel variants used as alternative priors in A5 and A6: C-LB-all, C-LB-secure, C-preGreek, C-Cypriot (if T1 is feasible).

### A5 to-do
- [ ] A5.1 Clone NeuroDecipher; extract the Linear B–Greek and Ugaritic–Hebrew data; record licences and versions.
- [ ] A5.2 Check Luo et al. 2021 code and Gothic/Iberian data availability.
- [ ] A5.3 C: Build the Greek → phonemic Mycenaean conversion; document rules.
- [ ] A5.4 C: Implement and train the channel model; k-fold validation.
- [ ] A5.5 C: Compile the secure-pair subset; train C-LB-secure; report the parameter shift (C1).
- [ ] A5.6 C: Compile and verify the pre-Greek Cretan toponym list; run T2.
- [ ] A5.7 C: Find an open digital Cypriot syllabary corpus; if found, run T1; if not, record the gap.
- [ ] A5.8 C: Run T3 on the direct Linear A ↔ Linear B pairs.
- [ ] A5.9 C: Freeze and hash the channel variants.
- [ ] A5.10 P: Build the per-sign feature distributions (PanPhon / sound classes) with explicit uncertainty; build the lattice expander.
- [ ] A5.11 Implement the degradation pipeline (A5.2 conditions) with each factor adjustable.
- [ ] A5.12 Port M1 (Finding 001) into the benchmark; add M2, M3, M5 (and M4 if available).
- [ ] A5.13 Pre-register the full evaluation protocol (conditions, metrics, success thresholds) in the hypothesis log.
- [ ] A5.14 Run the benchmark on known pairs across the degradation grid; produce the success and permissiveness curves.
- [ ] A5.15 Decide the phase gate: does any method keep measurable power at Linear A's conditions? Record the answer as a finding either way.
- [ ] A5.16 Publish the benchmark (code, data provenance, protocol) in the repo so third-party claims can be run through it.

---

## A6 — Typological profiling under script uncertainty

**Goal.** Posterior estimates (credible intervals, not point claims) for basic Minoan sound-structure properties, with spelling uncertainty modelled explicitly:
- Q6.1 Does the rarity of *o* survive once the spelling channel is modelled, or is it a script effect?
- Q6.2 Is the data compatible with a three-vowel system (a, i, u) under any plausible channel, or does it require five?
- Q6.3 How often were codas and clusters hidden by the spelling (the PA-I-TO ~ Phaistos type)?
- Q6.4 Is there evidence for an l/r contrast, or for missing series (e.g. labio-velars)?

**Model.** A generative model: an underlying phonotactic model (parameters: vowel inventory and frequencies, coda probability, cluster probability, consonant series) passes through a spelling channel from A5.C and produces observed sign strings. Inference by approximate Bayesian computation (simplest on a PC) or exact likelihood via transducer composition.

**Channel uncertainty.** Run with each channel variant (C-LB-all, C-LB-secure, C-preGreek, C-Cypriot) as an alternative prior, and report results per channel plus a pooled sensitivity summary. If the conclusion flips between channels, that is the result.

**Validation on known scripts.**
- Linear B: recover the Greek five-vowel system and approximate coda frequency from spellings alone.
- Cypriot syllabary (if T1 data exists): recover the same Greek phonology through a different channel. This is the strongest test.

**Stratification.** Run separately by register (administrative names vs libation formula) and by site, since the corpus may mix scribal conventions or even languages.

**Note.** The existence of o- and e-series signs in a script developed for Minoan is a qualitative argument (Steele 2024, Salgarella 2025). Record it as background; do not count it twice by also putting it into the prior.

To-do:
- [ ] A6.1 Specify the generative model and its parameters; log Q6.1–Q6.4 as H-A6-01…04 with decision rules.
- [ ] A6.2 Implement simulation and inference (ABC first).
- [ ] A6.3 Validate on Linear B (and Cypriot if available).
- [ ] A6.4 Run on Linear A with each channel variant; sensitivity analysis.
- [ ] A6.5 Run register- and site-stratified versions.
- [ ] A6.6 Write up with credible intervals per channel and an explicit statement of which conclusions are robust to channel choice.

---

## A7 — Script-relation analyses (palaeography)

**Goal.** Quantify sign-shape relations Hieroglyphic → Linear A and Linear A → Cypro-Minoan, following the approach of Corazza, Tamburini, Valério & Ferrara 2022 (unsupervised deep learning on sign images).

**Inputs.** SigLA tracings (licence check, A1.2); Cretan Hieroglyphic sign images (CHIC is print-only and paywalled, so availability is a risk); Cypro-Minoan signary (e.g. Polig & Donnelly 2025) and corpus images; licensing to be checked for all of them.

**Method.** Shape embeddings (self-supervised or pretrained CNN features, plus simple geometric descriptors as a baseline); nearest-neighbour correspondence and clustering.

**Validation on a known answer.** Linear A → Linear B sign correspondences (Salgarella 2020): does the embedding recover the known homomorph pairs above chance?

**Null models.** Random sign pairings; label permutations.

**Initial hypotheses.** H-A7-01 (validation): the embedding recovers Linear A–Linear B homomorphs above chance. H-A7-02: proposed Hieroglyphic antecedents (Ferrara, Montecchi & Valério 2022/2023) are more similar than random pairs. H-A7-03: proposed Linear A–Cypro-Minoan correspondences (Valério 2016/2024) are more similar than random pairs.

To-do:
- [ ] A7.1 Check image licensing for SigLA tracings, Hieroglyphic and Cypro-Minoan sources.
- [ ] A7.2 Build the image dataset (one record per sign occurrence, with source and licence).
- [ ] A7.3 Validate on Linear A → Linear B (H-A7-01). Stop if it fails.
- [ ] A7.4 Run H-A7-02 and H-A7-03.
- [ ] A7.5 Write up.

---

## Open verification items (resolve before relying on them)
- [ ] V1 SigLA licence (reported CC BY-NC-SA 4.0 secondhand) — A1.2.
- [~] V2 lineara.xyz licence — A1.3. No LICENSE file (2026-11-04); maintainer not yet asked.
- [~] V3 DAMOS raw-data availability and terms — A1.10. Content CC BY-NC-SA 4.0; downloads limited to word-search CSV (Aurora 2024, p. 157); no bulk export yet. Options in DATA_SOURCES.
- [ ] V4 Luo et al. 2021 code and Gothic/Iberian data — A5.2.
- [ ] V5 jhnwnstd/shannon lexicon: sources and quality.
- [ ] V6 An open digital corpus of the Cypriot syllabary (none identified yet) — needed for T1 and A6 validation.
- [~] V7 Corazza et al. 2021 supplementary data (list of tablets and constraints used). Open copy found (CC BY-NC-ND 4.0); no supplementary data or code located; no per-tablet constraint list in the paper. Details in DATA_SOURCES; to be verified against the PDF.
- [~] V8 Readable text of KN Zg 57/58. A descriptive overview is available, open access (CC BY-NC-SA 4.0): Kanta, Nakassis, Palaima & Perna 2025, *Ariadne* Suppl. 5, 27–43, doi:10.26248/ariadne.vi.1841. It has no sign-by-sign transcription. Still waiting for *Anetaki II* (Kanta ed., forthcoming).
- [ ] V9 Access to Salgarella 2025 (Cambridge Elements; paywalled unless free period).

## Change log
- 2026-10-31 — v1 created from survey §9. Added decisions D1 (no TTS/audio) and D2 (learned spelling channel with caveats C1–C3 and transfer tests T1–T3) to A5 and A6.
- 2026-11-02 — v1.1. A2.9 revised to a fraction-order test (H-A2-06, H-A2-07), because the sceptre has no totals and the ring has no numerals. V8 partly resolved; A1.13 updated to match. Blinding breach on KN Zg 57/58 recorded in `research-notes.md`; blinded-check rule added to §0.4; register/hand caveat added to A4.6.
- 2026-11-04 — v1.2. Repo created (A1.1 mostly done); hypotheses are now one file each in `hypotheses/`. lineara.xyz pinned and found to contain the held-out sceptre records (excluded via `data/heldout.txt`). A1.3, A1.5, V2 updated.
