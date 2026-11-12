# Phase 2 Analysis Plan & To-Do (derived from Literature Survey §9)

Version 1.3 — updated 2026-11-10 (v1 created 2026-10-31; v1.1 2026-11-02; v1.2 2026-11-04). Supersedes §9 of the Phase 1 literature survey as the working plan. The survey itself remains a dated snapshot (status as of October 2026).

How to use this file:
- Each analysis has an ID (A1–A9; A8 and A9 added 2026-11-10). Tasks are numbered A<n>.<m>. Use these IDs in the hypothesis log, commit messages and findings files.
- Hypotheses get IDs of the form H-A<n>-<nn> and are logged *before* the test is run (Rule 3), as one file each in `hypotheses/` (see `hypotheses/README.md`).
- Status markers: `[ ]` open, `[~]` in progress, `[x]` done, `[-]` dropped, `[p]` parked: not scheduled, may be reopened (reason in the change log).
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
  - A random 20% of documents, stratified by site and support type, is frozen as a confirmatory split for A3 and A4. **Frozen 2026-11-11 (A1.12):** 90 documents; strata with fewer than five documents are wholly training (`docs/heldout-split.md`).
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

### 0.6 Revised order (decided by Marius 2026-11-10, after the project review)
This order replaces the "suggested order" in §0.5 wherever they differ. The dependency diagram still holds.

**Ordering rules:** (1) protect blindness first; (2) unblock dependencies; (3) run cheap Linear A-only tests while the Linear B control is pending; (4) expensive or uncertain work last.

| # | Task(s) | Why here | Needs |
|---|---|---|---|
| **Stage 0: enabling** | | | |
| 1 | A1.12 freeze the held-out split, tag v1.0 | Every analysis run before the freeze spends blindness | — |
| 2 | A1.10 Linear B control (DAMOS; NeuroDecipher data as a stopgap) | Unblocks nearly every validation step | Marius's DAMOS check |
| 3 | A1.11 baseline statistics (training split only) + A1.14 resampling harness | Shared infrastructure; honest error bars for everything after | 1 |
| 4 | V10 check the January 2026 "meanings without decipherment" report | May pre-empt or inform A8.8 | — |
| **Stage 1: Linear A only, cheap** | | | |
| 5 | A8.1 labelled-picture gold set | Answer key for A8.2, A8.3 and A8.8 | 1 |
| 6 | A9.1–A9.2 audit of published quantitative claims | Highest chance of clear results, either way | 1, 3 |
| 7 | A5.17 benchmark Tier 1 (false-positive rates) | Main goal; Finding 001 has the code and a Linear B word control | 1 |
| 8 | A8.2 commodity association; A8.3 abbreviation test | No sound values; outputs feed A8.8 | 1, 3, 5 |
| 9 | A8.4 fraction sign by commodity; A8.5 roster order | Small, self-contained tests | 1, 3 |
| **Stage 2: needs Linear B** | | | |
| 10 | A3.4 affix go/no-go on subsampled Linear B, then A3 (with A3.8) | One cheap test decides whether A3 is worth running | 2 |
| 11 | A8.6–A8.8 role classifier, with genre clustering and ration structure as inputs | Main positive track | 2, 8 |
| 12 | A4 sign-value testing | Everything on L1 assumes Linear B values transfer | 2 |
| 13 | A9.3 one language across sites? | Needs the Knossos–Pylos baseline | 2, 3 |
| **Stage 3: after results exist** | | | |
| 14 | A5 Tier 2 (power curves, spelling channel A5.C) | Expensive; feasibility judged at roughly 50–60% | 2, 7 |
| 15 | A3.9 onomastic link | Needs name tagging and tested sign values | 2, 12 |
| 16 | A5.18 constrained substrate matching | Needs commodity results and the Tier 1 nulls | 7, 8 |
| 17 | A8.9 sealings; A8.10 word-division check | Lowest expected signal of the kept items | 8 |

**Main goal:** A5 Tier 1 plus the role classifier (A8.8); A5 Tier 2 is a stretch goal.

**Parked `[p]`:** A6 (typology), A7 (palaeography), A2.3, A2.4, A2.6, A2.7. Why: A6 and A7 are costly, have many free parameters, and nothing else depends on them; for A2, Finding 002 showed the totals have no power and the value-set tests are no longer blind. A parked task may be reopened by a change-log entry giving the reason. The A2 re-run on corpus-v1.0 is kept only as an automated regression check. The sceptre tests (A1.13, H-A2-06) stay registered and wait for *Anetaki II*.

**Considered and left out (2026-11-10):** Cretan Hieroglyphic as extra corpus material (sign correspondences uncertain); Egyptian renderings of Keftiu names (too few items to test); a model to restore damaged signs (corpus too small to train; restored signs could never count as evidence); synthetic expansion of the corpus (adds no information; allowed only as null corpora, degraded Linear B and resampling).

**Held-out budget.** The frozen split holds 90 documents (A1.12, 2026-11-11: 20% of the 450 documents in strata of five or more; v1.3 estimated about 114 before the small strata were counted), so confirmatory power is scarce. Before running items 6, 8 and 9, pre-register which of their hypotheses get a held-out test; the rest are exploratory.

**Estimates in this section are judgement, not measurement** (Rule 5): the signal ratings behind the order have not been tested.

### 0.7 Why and how: tasks added or brought forward in v1.3
Each entry says why the task exists and how to carry it out. "How" is a proposed design, to be fixed in the hypothesis file or the PR that does the work; it is Claude's suggestion (Rule 5), not a tested recipe. A8 and A9 tasks are elaborated in their own sections.

**A1.12 — Freeze the held-out split, tag v1.0 (first)**
- *Why.* A confirmatory test is only worth something if the data it runs on had not been looked at when the hypothesis was written. Each analysis run on the whole corpus removes that option for the documents it touched.
- *How.*
  1. Draw 20% of the 568 documents in the default analysis set, stratified by site and support type (plan §0.4), with a seed committed beforehand in the PR description.
  2. Write the document IDs to the held-out list. `data/heldout.txt` is a rule file, so this PR is merged by Marius.
  3. Make the corpus loader exclude the split by default; reading it requires an explicit flag that names a frozen hypothesis ID.
  4. Tag `corpus-v1.0` with a changelog.
- *Limits to state in the changelog.* A1.6–A1.9 and A2 have already processed every document, so the split is blind only for hypotheses written after the freeze. Nothing from A2 can be confirmed on it. Strata with fewer than five documents cannot be split meaningfully; put them wholly in the training set and say so.

**A1.10 — Linear B control corpus (Marius; stopgap allowed)**
- *Why.* Rule 4: every method is run on a script whose answer is known before it is trusted on Linear A. Items 10–13 and 14–15 of §0.6 cannot start without it.
- *How.* DAMOS is the target because it carries word roles and name tagging (needed for A8.8 and A3.9). If no bulk export is available, use the Linear B–Greek data in the NeuroDecipher repository as a stopgap for tasks that need only word lists (A3.4, A5.17), after recording its licence and source (A5.1). A stopgap result is re-run on DAMOS when it arrives.

**A1.11 — Baseline statistics, on the training split only**
- *Why.* Sign frequencies, positional counts and length distributions are the inputs to A3, A4, A8 and A9. Computing them on the full corpus would leak the held-out split into every later hypothesis.
- *How.* As already described under A1, but run after A1.12 and on the training split. Report each figure per witness (lineara.xyz, SigLA, Younger) where they differ, not for a merged text.

**A1.14 — Resampling harness**
- *Why.* The witnesses disagree on about 2% of signs (A1.9), and many tablets are damaged. A result that flips when a doubtful sign is read the other way is not a result. Bootstrapping documents also shows whether a pattern rests on two or three tablets, as the fraction-order evidence partly did (Finding 002).
- *How.*
  1. One function that takes an analysis (a callable returning a statistic) and returns its distribution over (a) draws in which each disputed or doubtful sign takes one of its attested readings, and (b) bootstrap samples of documents, stratified by site.
  2. Every stochastic step takes a recorded seed.
  3. Findings report the interval alongside the point estimate.
- *Not for.* Resampled text is never added to the corpus and never counts as extra evidence (CLAUDE.md, rule 9).

**A1.15 — Report likely lineara.xyz errors upstream (optional)**
- *Why.* A1.9 found probable errors (CAP where two other sources have OVIS, 13–14 times; Arkhanes tablets under a wrong site label). Reporting them improves a source others use, and a maintainer's reply is an independent check on our reading of the data.
- *How.* Check each case on the GORILA facsimile first, list the confirmed ones in a short issue for the lineara.xyz repository, and ask the licence question (A1.3) in the same message. Marius sends it; an agent drafts it only.

**A3.4 — Affix go/no-go on subsampled Linear B (before the rest of A3)**
- *Why.* If the segmenters cannot recover known Greek endings from a Linear B sample the size of Linear A, running them on Linear A would produce output with no way to judge it. This one test decides whether A3.5–A3.7 are worth doing.
- *How.* As in the A3 section. Use the NeuroDecipher word list if DAMOS is not yet available, and say which was used. Fix the success threshold (precision and recall against the frozen gold list, A3.2) before running. A fail is recorded as a finding and A3 stops there.

**A3.8 — Libation formula as aligned text**
- *Why.* The formula recurs on stone vessels from several sites with small variations. Where one slot varies while its neighbours stay fixed, the variants are minimal pairs: the best evidence for prefixes and endings that this corpus can offer. It is also the material behind the published word-order and prefix claims (A9.1).
- *How.*
  1. List the formula's inscriptions from the canonical document list (support type and register fields), training split only.
  2. Align them slot by slot at L0 with a standard sequence-alignment method; record every alignment decision.
  3. For each slot, tabulate the variants and test whether the variation is concentrated at the start or end of the sign-group more than the A3.3 nulls predict.
- *Limits.* A few dozen short inscriptions, some damaged. Report counts, not percentages, and treat everything beyond the pre-registered A3 hypotheses as exploratory.

**A3.9 — Onomastic link to the non-Greek names in Linear B**
- *Why.* The Knossos Linear B tablets record many personal names that are not Greek. If they continue the Minoan naming stock, they are the largest body of probably-Minoan material outside Linear A, and the link can be tested instead of assumed.
- *How.*
  1. From DAMOS, take personal names at Knossos and split them into Greek and non-Greek by the editors' classification (frozen list, source recorded).
  2. Take the Linear A sign-groups that A8.8 classifies as name-like.
  3. Compare sign n-grams at the end and at the start of the groups between the two sets, at L0 and L1.
  4. Nulls: the Greek names at Knossos; non-Greek names from Pylos (a mainland control); sign-shuffled names.
- *Depends on.* A1.10 with name tagging, A8.8, and the A4 result on whether Linear B values hold for Linear A. If A4 fails, run at L0 only.
- *Risk.* "Non-Greek" is an editorial judgement and may itself rest on resemblance to Linear A; record how the source decided.

**A5.17 — Benchmark Tier 1: false-positive rates (main goal, part 1)**
- *Why.* Finding 001 showed that one published method matches random lexicons as well as its target language. The same question can be asked of any lexical-matching method, and the answer is a number: how often does it "find" a language that is not there? This needs little compute and no new data.
- *How.*
  1. Define a common interface: a method takes a sign-group list and a lexicon and returns matches.
  2. Port the Finding 001 matcher as the first method (A5.12, M1); add the others as they are implemented.
  3. For each method and each candidate lexicon, run: the real lexicon; random pseudo-lexicons with the same size and letter frequencies; and Linear B words of known Greek meaning in place of Linear A.
  4. Report the match rate against each null, and count the method's degrees of freedom using the checklist in `docs/guardrails.md`.
  5. Pre-register the protocol (A5.13) before adding any method beyond M1.
- *Output.* A table per method and a script that takes a new claim's rules and lexicon, so third-party claims can be run through it (A5.16).
- *Tier 2* is the existing A5.11–A5.14 (degradation grid and power curves) plus the spelling channel (A5.C).

**A5.18 — Constrained substrate matching**
- *Why.* Open lexical matching fails because the choice of meaning is free. Where a Linear A word stands next to a commodity logogram, its semantic field is fixed before any comparison, which removes that freedom.
- *How.*
  1. From A8.2, take the Linear A words tied to one commodity. Freeze the list.
  2. From a published list of pre-Greek loanwords in Greek (source to be chosen and recorded), take only words in the same semantic fields. Freeze that list too.
  3. Compare within field only, with the A5.17 nulls: random lexicons, and the same words matched against the wrong field.
- *Expect.* A dozen candidates at most, so one or two survivors at best; a result of none is recorded. Published proposals of this kind exist (for example for sesame and for figs); their sources are to be verified in the task, not taken from this plan.

**V10 — Check the January 2026 report**
- *Why.* The headline describes recovering Linear A meanings without deciphering the language, which is what A8 attempts. It may pre-empt A8.8, supply a baseline, or use a method worth validating.
- *How.* Identify the underlying publication. Before reading it, check from its abstract or title alone that it does not treat the held-out sceptre; if it does, a separate agent returns only pre-specified fields (plan §0.4). Record in research-notes what it does and what changes in A8.

---

## A1 — Canonical, versioned Linear A corpus

**Goal.** One canonical, documented, versioned corpus that every later analysis uses, with explicit inclusion rules and provenance.

**Why.** Published document counts disagree (1,427 in the Linear A Digital Corpus; 1,534 per RILA Suppl. 1 as cited by Navarre-AI; 772–787 in SigLA harvests). Without a fixed list, no result is reproducible.

**Sources.** SigLA (preferred machine-readable source), lineara.xyz (already used in Finding 001), Younger's transliterations, GORILA sigla as universal keys. Control corpus: DAMOS (Linear B).

**Deliverables.** `data/` with raw snapshots + processed corpus; `docs/schema.md`; `DATA_SOURCES.md` (source, version/date, licence, conventions); tagged release v1.0; baseline statistics report.

To-do:
- [x] A1.1 Set up the GitHub repo structure (https://github.com/marius-vrancianu/aegean-scripts): `data/raw`, `data/processed`, `src/`, `notebooks/`, `findings/`, `hypotheses/`, `research-notes.md`, `DATA_SOURCES.md`, `CLAUDE.md`, CI guardrails. Done 2026-11-04, including the Finding 001 code (`experiments/finding-001/`, reproduced exactly).
- [x] A1.2 Verify the SigLA licence directly on the site (survey reports CC BY-NC-SA 4.0 secondhand). Record exact terms and what redistribution is allowed. **Done 2026-11-06:** CC BY-NC-SA 4.0, verified in the site footer. Redistribution is allowed with attribution, non-commercially, and ShareAlike applies to corpus files derived from SigLA (see DATA_SOURCES).
- [~] A1.3 Establish the lineara.xyz licence. 2026-11-04: the repo has no LICENSE file (all rights reserved by default), so we fetch rather than commit. Still to do: ask the maintainer. Record it for Finding 001's data provenance too.
- [x] A1.4 Harvest SigLA: documents, sign tokens, sign roles (syllabogram/logogram/numeral/fraction/ligature), word division, findspot/support metadata. Store a dated raw snapshot with a content hash. **Done 2026-11-10:** `database.js` (OCaml Marshal, not JSON) committed at `data/raw/sigla/0c4ef69f5de4/`, with SHA256SUMS. Reader: `aegean.corpus.sigla`. 827 documents, 5,184 attestations. **SigLA has no numeral values**, so lineara.xyz stays the numeral source. No JE ligature in SigLA. Findspot is site-level only. Layout and caveats: `data/raw/sigla/README.md`.
- [x] A1.5 Snapshot lineara.xyz (`LinearAInscriptions.js`, commit hash) and Younger's transliteration pages (date of access). lineara.xyz pinned 2026-11-04 (`data/raw/lineara.xyz/fetch.py`). **The snapshot contains the sceptre records; see `data/heldout.txt` and research-notes 2026-11-04.** **Younger done 2026-11-10:** the KU site is gone, so his 2024 Academia.edu PDFs are pinned instead (`data/raw/younger/SHA256SUMS`; not committed, no licence). Reader: `aegean.corpus.younger`, 503 entries. **Non-HT only:** Younger's HT file could not be found, so HT has two sources (SigLA, lineara.xyz) in A1.9.
- [x] A1.0 (added 2026-11-04) Provisional single-source release **corpus-v0.1**: lineara.xyz only, L0, held-out excluded; built by `python -m aegean.corpus.build`, hashes in `data/processed/corpus-v0.1/MANIFEST.json`. For A2 until corpus-v1.0; every A2 result on it carries the single-source caveat and is re-run on v1.0.
- [x] A1.6 Reconcile the document lists. Write explicit inclusion rules (support type, minimum legibility, site, period, register) and produce one canonical list keyed by GORILA siglum. **2026-11-10:** concordance and canonical list built (`python -m aegean.corpus.document_list`): 1,619 documents, 568 in the proposed default analysis set. Rules in `docs/inclusion-rules.md`. **Decided by Marius 2026-11-10:** T1 only in analyses; single-source documents kept; lost `<n>` documents kept out. Other rules keep their proposed defaults.
- [x] A1.7 Define the schema: document → line (where known) → sign-group → sign token. Fields per token: GORILA sign ID, role, damage/uncertainty flag, alternative readings with their source. Fields per document: site, support, period (LM IB etc.), register (administrative / religious / other), scribal hand where published. **Done 2026-11-10:** `docs/schema.md`, `aegean.corpus.schema`, `aegean.corpus.witnesses`. Document → witness (one per source, never merged) → line → item → token. Alternative readings are the other sources' witnesses. Canonical sign IDs follow GORILA/Bennett; ligatures keep both the single sign and its components; None vs False marks what a source does not record. All 3,049 witnesses validate. Younger's values map to sign IDs in A1.8.
- [x] A1.8 Build layers L0 and L1 (L2 comes from A5). **Done 2026-11-10:** `docs/layers.md`, `aegean.corpus.layers`, `python -m aegean.corpus.build_layers` → `data/processed/corpus-v1.0-pre/`. L0: Younger values mapped to sign IDs (2,709 of 3,035 tokens), validated against SigLA on 335 shared documents (98.8% agreement). L1: uniform Unicode Linear B values from L0; undeciphered and Linear A-only signs kept as numbers.
- [x] A1.9 Cross-source disagreement report: list every place where SigLA, Younger and lineara.xyz differ. This is a data-quality result in its own right. **Done 2026-11-10** as a data-quality report (Marius's choice), not a finding: `docs/reports/A1.9-source-disagreements.md`, built by `python -m aegean.corpus.disagreements`. Identified signs agree 97.5–98.7% between pairs of sources. **HT numerals and fractions effectively rest on lineara.xyz alone.** lineara.xyz appears to have OVIS/CAP and site-name errors; SigLA omits fractions on 57 documents.
- [ ] A1.10 Linear B control corpus: check whether DAMOS offers raw data download (its developers have said they plan to release raw data); otherwise request it or harvest the online version within its terms. Keep its lemma/normalisation layers.
- [~] A1.11 Baseline statistics: sign frequencies, positional statistics (initial/medial/final), sign-group length distribution, breakdown by site/period/register. Re-derive Packard-style figures as a sanity check. **2026-11-10:** order and design revised, see §0.6 and §0.7. **2026-11-11:** code done (`aegean.corpus.baseline`, training split, per source, L0); report `docs/reports/A1.11-baseline-statistics.md` is a **partial build** (lineara.xyz and SigLA; Younger needs a run on the machine with the PDFs). Still open: the Younger column, the comparison with Packard's published figures, period labels not normalised.
- [x] A1.12 Freeze the held-out split (§0.4), then tag release v1.0 with a changelog. **2026-11-10:** order and design revised, see §0.6 and §0.7. **Done 2026-11-11:** 90 documents held out (20% of each of the 22 strata with five or more documents; 88 smaller strata, 118 documents, wholly training), seed 20261111. Procedure: `docs/heldout-split.md`; changelog and limits: `docs/corpus-changelog.md`; loader: `aegean.corpus.load`. Marius creates the `corpus-v1.0` tag on the merge commit.
- [ ] A1.13 When a readable edition text of KN Zg 57/58 is available (the 2025 *Ariadne* overview has no sign-by-sign transcription; wait for *Anetaki II*), add it under the held-out flag.
- [x] A1.14 (added 2026-11-10) Resampling harness: rerun any analysis across (a) the alternative readings of damaged or doubtful signs given by the other witnesses and (b) bootstrap samples of documents, so results carry intervals that reflect reading uncertainty. Shared by A3, A4, A8 and A9. Why and how: §0.7. **Done 2026-11-11:** `aegean.corpus.resample` (reading draws by source per document plus doubtful-sign blanking; document bootstrap within sites; both). Bootstrap intervals are biased low for counts of distinct types; see the A1.11 report.
- [ ] A1.15 (added 2026-11-10, optional) Report the likely lineara.xyz errors from the A1.9 report upstream (OVIS/CAP, the Arkhanes site label), after checking them on GORILA. Marius sends the message. Why and how: §0.7.

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
- [x] A2.2 List every document with KU-RO, KI-RO or PO-TO-KU-RO; classify each as complete / damaged / indeterminate. 2026-11-04: rule-based inventory on corpus-v0.1 (`experiments/A2/inventory-corpus-v0.1.csv`, rules in `inventory-rules.md`): 55 marker occurrences in 42 documents; 9 complete, 7 complete-scope-unclear. **Still to do:** check each candidate row against the GORILA facsimile, because the source's damage flags are incomplete. **GORILA check completed 2026-11-05** for all 39 KU-RO / PO-TO-KU-RO occurrences (`experiments/A2/gorila-checks/`). KI-RO rows still to check (needed for H-A2-03).
- [p] A2.3 Reproduce Corazza et al. 2021. **Revised 2026-11-04 (V7):** their values were not fitted to tablet totals. They come from six premises solved in MiniZinc/Gecode (2,172,836 / 3,794,740 solutions), then ranked by frequency, typology and optimality, with HT 104 and PE 1 cited only as support. So: (a) the reproduction target is their solution counts and final ranking under their premises (needs the premises verified from the PDF); (b) H-A2-01, whether their value set makes tablet totals more consistent than random value sets do, is a **new** test, not a reproduction.
- [p] A2.4 Build the Linear B *to-so* validation set and run the checker. Source route (V3): DAMOS word-search CSV for *to-so* plus the online texts of those tablets (CC BY-NC-SA 4.0), or a data extract requested from the editor.
- [~] A2.5 Log H-A2-01…05 with exact test definitions and tolerance rules. Batch 1 (2026-11-04): H-A2-04 (HT 122 sanity check) and H-A2-07 (fraction-order consistency, value-free primary test). H-A2-01/02/03/05 wait until each candidate row in the inventory has been checked against GORILA, because their scope and tolerance rules depend on that check. **Run 2026-11-05:** H-A2-07 supported (outcome file); H-A2-04 inconclusive. HT 122 does not add up as read (31 + 65 = 96 vs PO-TO-KU-RO 97), and the 97 touches edge damage. **2026-11-05: exploratory full census run** (`experiments/A2/exploratory/`). H-A2-01/02 can no longer be blind on corpus-v0.1, and totals there cannot discriminate between value sets; confirmatory tests move to new data.
- [p] A2.6 Run the value-set comparison and the null distributions.
- [p] A2.7 Run the KI-RO relation test.
- [x] A2.8 Write up: a table of every total (consistent / inconsistent / indeterminate) under each value set, plus the null comparison. **Brought forward 2026-11-05 as H-A2-08** (integer-only census with observable categories and a chance baseline; proposed by Marius). Fraction-bearing totals are passed to H-A2-01/02. **Run 2026-11-05: not supported, i.e. uninformative** (corrected 2026-11-06 from "inconclusive": exact p = 0.0500, and the minimum attainable p was 0.05, so the test had no power). 5 testable totals: 2 consistent, 1 off by one, 2 inconsistent with likely scope causes. 32 of 37 KU-RO totals are untestable as transmitted.
- [~] A2.9 (revised 2026-11-02) **Sceptre fraction-order test (held-out).** KN Zg 57 has no numerals. KN Zg 58 face δ has vases, units and six distinct fraction signs in sequence, and no total word is reported (Kanta et al. 2025, pp. 40–42). The original total-consistency test is therefore impossible. Replacement test: 2026-11-05: precondition H-A2-07 **supported** (C = 1.00, p < 0.0001), so H-A2-06 can be registered once the A2 value set is frozen. **H-A2-06 registered 2026-11-06** in value-free form (frozen corpus order graph); waits for *Anetaki II*.
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
- [ ] A3.8 (added 2026-11-10) Libation formula as aligned text: align the repeated formula across its inscriptions and treat the variant slots as minimal pairs for affix discovery, against the A3.3 nulls. Small sample; report it as such. Why and how: §0.7.
- [ ] A3.9 (added 2026-11-10) Onomastic link: test whether Linear A name-like sign-groups (from A8.8) share endings with the non-Greek personal names on the Knossos Linear B tablets more often than a null predicts. Needs DAMOS name tagging (A1.10) and the A4 result on sign values. Uses L1. Why and how: §0.7.

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
- [ ] A5.17 (added 2026-11-10) **Tier 1, brought forward: false-positive benchmark.** Generalise Finding 001: run each lexical-matching method against random pseudo-lexicons and against Linear B words of known Greek meaning, and report its false-positive rate and degrees of freedom. Does not need DAMOS. A5.11–A5.14 (degradation grid, power curves) are Tier 2. Why and how: §0.7.
- [ ] A5.18 (added 2026-11-10) Constrained substrate matching: compare only Linear A words whose commodity is fixed by a logogram (from A8.2) with pre-Greek loanwords in Greek from the same semantic field. Candidate list and semantic fields are frozen before comparison; nulls as in A5.17. Expect a dozen candidates at most. Why and how: §0.7.

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
- [p] A6.1 Specify the generative model and its parameters; log Q6.1–Q6.4 as H-A6-01…04 with decision rules.
- [p] A6.2 Implement simulation and inference (ABC first).
- [p] A6.3 Validate on Linear B (and Cypriot if available).
- [p] A6.4 Run on Linear A with each channel variant; sensitivity analysis.
- [p] A6.5 Run register- and site-stratified versions.
- [p] A6.6 Write up with credible intervals per channel and an explicit statement of which conclusions are robust to channel choice.

---

## A7 — Script-relation analyses (palaeography)

**Goal.** Quantify sign-shape relations Hieroglyphic → Linear A and Linear A → Cypro-Minoan, following the approach of Corazza, Tamburini, Valério & Ferrara 2022 (unsupervised deep learning on sign images).

**Inputs.** SigLA tracings (licence check, A1.2); Cretan Hieroglyphic sign images (CHIC is print-only and paywalled, so availability is a risk); Cypro-Minoan signary (e.g. Polig & Donnelly 2025) and corpus images; licensing to be checked for all of them.

**Method.** Shape embeddings (self-supervised or pretrained CNN features, plus simple geometric descriptors as a baseline); nearest-neighbour correspondence and clustering.

**Validation on a known answer.** Linear A → Linear B sign correspondences (Salgarella 2020): does the embedding recover the known homomorph pairs above chance?

**Null models.** Random sign pairings; label permutations.

**Initial hypotheses.** H-A7-01 (validation): the embedding recovers Linear A–Linear B homomorphs above chance. H-A7-02: proposed Hieroglyphic antecedents (Ferrara, Montecchi & Valério 2022/2023) are more similar than random pairs. H-A7-03: proposed Linear A–Cypro-Minoan correspondences (Valério 2016/2024) are more similar than random pairs.

To-do:
- [p] A7.1 Check image licensing for SigLA tracings, Hieroglyphic and Cypro-Minoan sources.
- [p] A7.2 Build the image dataset (one record per sign occurrence, with source and licence).
- [p] A7.3 Validate on Linear A → Linear B (H-A7-01). Stop if it fails.
- [p] A7.4 Run H-A7-02 and H-A7-03.
- [p] A7.5 Write up.

---

## A8 — Functional meaning without sound values (added 2026-11-10)

**Goal.** Assign functional categories to Linear A sign-groups (a commodity qualifier, a person, a transaction term) from their position, their logograms and their numbers. The output is of the form "this word behaves like a kind of oil" or "this word behaves like a personal name". It is not a translation and makes no claim about the language.

**Why it matters.** It is the one route to meaning that does not depend on sound values or on a related language, so it is not limited by the result of A5. Linear B supplies a labelled model of the same kind of bookkeeping, which gives every step a known-answer control.

**Layer.** L0 throughout. L1 is used only to name sign-groups in write-ups.

**Validation on a known script.** Each method is run on Linear B first, where the role of each word is known. Standing rules for that validation:
- Split by site (train on Knossos, test on Pylos, and the reverse), never at random. Tokens cluster by tablet, scribe and series, so a random split overstates accuracy.
- Degrade Linear B to Linear A conditions (short tablets, similar corpus size, only the features Linear A also has) and report how accuracy falls.
- Compare with a trivial baseline; if the method barely beats it, that is the finding.

**Standing caveats** (carry into every A8 result).
- **Circular labels.** Role labels in Linear B editions were assigned partly from these same contextual cues, so accuracy on Linear B overstates what the method knows.
- **Tiny answer key on Linear A.** A8.1, KU-RO, KI-RO, the logograms and the place names shared with Linear B: perhaps 20–40 items. Accuracy on Linear A will carry a wide interval.
- **Names versus places.** Both fill the same slots; in Linear B they are separated partly by Greek morphology. Expect this distinction to be weak.
- **Transfer.** Minoan and Mycenaean bookkeeping differ (Linear A entries are terser and use fractions differently). A method that works on Linear B is a hypothesis about Linear A, not a measurement.
- **Single source for HT numerals** (A1.9): any test using quantities at Haghia Triada rests on lineara.xyz alone.

**Hypotheses.** Each test below is registered as H-A8-nn before it runs. Because the held-out split is small (§0.6), each hypothesis file states whether the test is confirmatory (held-out) or exploratory (training split, FDR-controlled).

### A8 to-do

- [~] **A8.1 Labelled-picture gold set.** **2026-11-11: draft built, not frozen** (`python -m aegean.roles.gold`; `docs/reports/A8.1-gold-set.md`). 21 items, 16 usable for scoring; the five labelled pictures are all on HT 31. Before freezing: full three-source build, literature rows checked against the publications, grades confirmed by Marius.
  - *Why.* A few inscriptions write a word beside a drawn or logographic object, which gives the word's referent with no assumption about language. These are the only ground truth Linear A offers for A8, so they are collected and frozen first.
  - *How.* Search the witnesses for sign-groups written above, inside or directly beside a logogram (HT 31, a tablet of vessel signs with words written over them, is the standard example; the details are to be verified from the witnesses and GORILA, not from this plan). Record for each: document, sign-group at L0, the object, the source, and a confidence grade. Add KU-RO and KI-RO and the place names shared with Linear B, each with its published source. Freeze the list with a hash before A8.2 runs.
  - *Output.* `data/processed/gold/` plus a short report. No hypothesis needed (it is data).

- [ ] **A8.2 Commodity association.**
  - *Why.* A word that occurs only with oil, or only with small whole numbers of people, has told us something about what it denotes. Published work on the Haghia Triada archive has made such observations tablet by tablet; the test is whether they hold corpus-wide against chance.
  - *How.* For each sign-group that occurs at least a fixed minimum number of times (threshold set in the hypothesis file), tabulate the logograms in its entry and the size class of its number (fraction only, 1–9, 10–99, 100+). Measure the concentration of each word's distribution. Null: permute logograms among entries within the same document type and site, which keeps each tablet's commodity mix. Interval from A1.14.
  - *Validation.* Same procedure on Linear B, scored against the known meanings (commodity qualifiers, personnel terms).
  - *Output.* A table of words with a significant association, after FDR control; inputs to A8.8 and A5.18.

- [ ] **A8.3 Abbreviation test.**
  - *Why.* Linear B scribes abbreviate: a small syllabogram attached to a logogram, or standing alone before a number, is the first sign of a full word (for example *o* for *o-pe-ro*, "deficit", and *pa* attached to the cloth logogram for *pa-we-a*, a kind of cloth). Linear A has the same kind of compound signs (a logogram with a syllabogram attached). If they work the same way, each one links a full word to a commodity or a transaction type.
  - *How.* List every logogram-plus-syllabogram compound and every isolated syllabogram in entry position. For each, count the full sign-groups that begin with that sign and occur with the same logogram (in the same site first, then corpus-wide). Null: the same count with the attached sign replaced by a random sign of similar frequency. Test statistic: how many compounds have at least one matching full word, against the null distribution.
  - *Validation.* Linear B, where the abbreviations are known: the method must recover them at Linear A's corpus size.
  - *Output.* Candidate word-to-commodity and word-to-transaction links, each labelled as a hypothesis.

- [ ] **A8.4 Fraction sign by commodity.**
  - *Why.* There are two readings of the Linear A fraction signs: pure fractions (the premise of Corazza et al. 2021) or units of measure, as in Linear B, where dry and liquid goods have different sub-units. If some signs occur only with dry goods and others only with liquids, the second reading gains support. Finding 002 showed totals cannot settle fraction questions; this test does not use totals.
  - *How.* Classify logograms as dry, liquid or counted (list frozen first, with sources). Build the contingency table of fraction sign against class. Test by permuting class labels among entries within site. Check the result survives dropping any one tablet.
  - *Validation.* The Linear B measure signs, which should separate cleanly.
  - *Limits.* Mostly Haghia Triada, so single-source numerals; few occurrences for the rarer signs. Likely outcome is "no power" for most signs, which is recorded.

- [ ] **A8.5 Roster order.**
  - *Why.* If the same names recur on several tablets in the same relative order, the tablets draw on a standing list (a roster or a hierarchy), which says something about what the lists are and supports reading the entries as persons or places. It is the same design as H-A2-07, which worked.
  - *How.* Take sign-groups that occur on two or more tablets. For every pair that co-occurs on two or more tablets, record whether the order is the same. Statistic: the share of consistent pairs. Null: shuffle entry order within each tablet.
  - *Validation.* Linear B personnel series, where recurring lists are documented.
  - *Limits.* Few words recur across tablets; state the number of usable pairs before interpreting.

- [ ] **A8.6 Genre clustering.**
  - *Why.* What a tablet records constrains what its heading and entries can mean. Linear B tablets fall into recognised series (personnel, livestock, rations, land); if Linear A tablets cluster the same way on structural features, each cluster gets a provisional genre.
  - *How.* Describe each tablet by its logogram profile, the size profile of its numbers, entry count, and the presence of total words. Cluster with a simple method (hierarchical or k-medoids); choose the number of clusters by a stability criterion fixed in advance.
  - *Validation.* On Linear B, the clusters must recover the known series better than a random partition (adjusted Rand index).
  - *Output.* A genre label per tablet, used as a feature in A8.8 and as the "document type" control in A8.2 and A9.3.

- [ ] **A8.7 Ration and ratio structure.**
  - *Why.* Rations and levies follow fixed scales. In Linear B, fixed amounts per person and fixed proportions between commodities are what identified ration tablets. Recurring ratios in Linear A mixed-commodity lists would identify allocations and, through them, the role of the heading words.
  - *How.* For tablets listing two or more commodities per entry, compute the ratios between them and test for clustering at simple values against a null that permutes quantities among entries. Separately, test whether particular amounts recur more often than a smooth distribution predicts.
  - *Validation.* The Linear B ration tablets.
  - *Limits.* Depends on fraction values for sub-unit amounts; run with whole numbers first, then with each published value set, and report both.

- [ ] **A8.8 Role classifier (main goal, part 2).**
  - *Why.* It combines the evidence above into one calibrated statement per sign-group, with an honest error rate measured on a script we can read.
  - *How.*
    1. Classes, coarse first: name-like (person or place), commodity or qualifier, transaction term, other. Finer classes only if the coarse ones validate.
    2. Features, all structural: position in the tablet and in the entry; what follows (logogram, number, another word); recurrence across tablets and across sites; group length; site, support type and period; and the outputs of A8.2, A8.3, A8.6 and A8.7.
    3. Model: logistic regression or a small tree ensemble. Nothing larger: the feature count is under a few dozen.
    4. Train on Linear B roles from DAMOS. Validate across sites and under degradation (see above). Baseline: "any word directly before a number is a name".
    5. Report calibrated probabilities; the model abstains below a threshold fixed in advance. Many Linear A groups occur once and will be abstentions.
    6. Apply to Linear A; score against the A8.1 gold set; propagate reading uncertainty with A1.14.
  - *Pre-registration.* The classes, features, threshold and success criteria on Linear B are registered before training. The Linear A predictions are frozen before they are compared with the gold set.
  - *Output.* A finding either way: the per-class accuracy on Linear B at Linear A's scale, and the list of Linear A sign-groups with a role and a probability.

- [ ] **A8.9 Single-sign sealings.**
  - *Why.* About 1,050 listed documents are outside the default analysis set; most carry a single sign or none, and many are sealings (exact counts by type from the document list). They are the largest unused part of the corpus. If their signs are the same ones used as logograms or abbreviations on tablets at the same site, the sealings and tablets belong to one accounting system, and the sealings add evidence to A8.3.
  - *How.* For each site with both sealings and tablets, compare the frequency distribution of sealing signs with (a) logograms, (b) attached and isolated syllabograms (A8.3) and (c) word-initial signs on the tablets. Null: sealing signs drawn from the site's overall sign frequencies.
  - *Limits.* Sealing types differ in function; stratify by type where the witnesses record it. Low expected signal.

- [ ] **A8.10 Word-division check.**
  - *Why.* Every analysis of sign-groups assumes the scribes' dividers mark words. On tablets that is fairly safe; on the libation inscriptions division is inconsistent.
  - *How.* Run an unsupervised segmenter (the Bayesian one from A3) on the undivided sign stream and compare its boundaries with the dividers (precision and recall).
  - *Validation.* Linear B, with dividers removed: the segmenter must recover them at Linear A's corpus size, or the task stops.
  - *Output.* An agreement figure per register, and a list of places where the segmenter and the scribe disagree, for A3.8.

---

## A9 — Audit of published claims; site comparison (added 2026-11-10)

**Goal.** Test the quantitative claims already in the literature against explicit nulls on corpus-v1.0, and test the assumption that the Linear A sites record one language.

**Why it matters.** Many statements about Linear A rest on counts made by hand on older editions, without a chance baseline. Each one is a ready-made hypothesis with a source. Results are useful whichever way they come out, and the work needs no sound values, no Linear B control (except A9.3) and little compute.

**Layer.** Stated per claim. Most are L0; claims about a prefix or a vowel are stated at L1 and tested at L0.

- [ ] **A9.1 Compile the claims.**
  - *Why.* The audit is only as good as its selection. Choosing claims after seeing which ones fail would be a free choice of the kind the guardrails forbid.
  - *How.* From the literature survey and its sources, list five to ten claims that state or imply a count. Candidates, each to be verified against its source before it is listed: verb-first word order in the libation formula; the alternation of an A- and a JA- prefix by context; pure-vowel signs occurring mostly at the start of words. For each, record the exact source and page, the claim in the author's terms, and its translation into a test: statistic, unit, null. Freeze the list before any is run. Access limits (V9) may exclude some sources; say which.
- [ ] **A9.2 Register and run.**
  - *Why.* Rule 3. Also, a batch of ten tests needs FDR control and a full count, failures included.
  - *How.* One hypothesis file per claim (H-A9-nn), reviewed as a batch. Run on the training split with A1.14 intervals. Confirm on the held-out split only the claims chosen for that in advance. Write one finding covering all of them. "Not supported" means the count does not beat the null on this corpus; it is not a refutation of the author's reading, and the write-up must keep the two apart.
- [ ] **A9.3 One language across sites?**
  - *Why.* Nearly all work pools Haghia Triada, Khania, Zakros, Phaistos and the rest as one "Minoan". If the sites differ by more than two sites of a single known language do, pooled statistics (A3, A4, A8) are mixing populations.
  - *How.* For each pair of sites with enough text, compare sign frequencies, positional profiles (initial, medial, final) and sign-pair frequencies, with a distance measure fixed in advance. Control for document type using A8.6 genres, since a site that records sheep will differ from one that records oil for that reason alone. Null: reassign documents to sites at random within genre.
  - *Validation and baseline.* The same comparison between Knossos and Pylos in Linear B: one language, two sites, different periods and scribes. That distance is the yardstick for "same language".
  - *Limits.* Haghia Triada dominates the corpus; most other sites may have too little text. State the minimum size at which the Linear B baseline can still tell the sites apart, and do not test Linear A sites below it.

---

## Open verification items (resolve before relying on them)
- [ ] V1 SigLA licence (reported CC BY-NC-SA 4.0 secondhand) — A1.2.
- [~] V2 lineara.xyz licence — A1.3. No LICENSE file (2026-11-04); maintainer not yet asked.
- [~] V3 DAMOS raw-data availability and terms — A1.10. Content CC BY-NC-SA 4.0; downloads limited to word-search CSV (Aurora 2024, p. 157); no bulk export yet. Options in DATA_SOURCES.
- [ ] V4 Luo et al. 2021 code and Gothic/Iberian data — A5.2.
- [ ] V5 jhnwnstd/shannon lexicon: sources and quality.
- [ ] V6 An open digital corpus of the Cypriot syllabary (none identified yet) — needed for T1 and A6 validation.
- [x] V7 Corazza et al. 2021: verified from the PDF 2026-11-05 (`docs/references/corazza-2021-notes.md`). No supplementary data or code; no per-tablet constraint list. Descending order is their premise 5.
- [~] V8 Readable text of KN Zg 57/58. A descriptive overview is available, open access (CC BY-NC-SA 4.0): Kanta, Nakassis, Palaima & Perna 2025, *Ariadne* Suppl. 5, 27–43, doi:10.26248/ariadne.vi.1841. It has no sign-by-sign transcription. Still waiting for *Anetaki II* (Kanta ed., forthcoming).
- [ ] V9 Access to Salgarella 2025 (Cambridge Elements; paywalled unless free period).
- [~] V10 (added 2026-11-10) A January 2026 news report describes scholars reconstructing Linear A meanings without deciphering the language (https://greekreporter.com/2026/01/15/reconstruct-linear-a-crack-language/; a Kadmos 2025 article appeared in the same search). Neither has been read: the page did not load. Identify the underlying publication and check whether it pre-empts or informs A8.8. Check first that it does not treat held-out material. Why and how: §0.7. **2026-11-11:** partly checked from search excerpts only (research-notes). The page shows the held-out sceptre in a photograph, so it needs a blinded read; no underlying publication identified yet; on what was seen it does not pre-empt A8.8. Two Kadmos 2025 articles (olive logogram; spice signs) noted for A8.2 and A8.1.

## Change log
- 2026-10-31 — v1 created from survey §9. Added decisions D1 (no TTS/audio) and D2 (learned spelling channel with caveats C1–C3 and transfer tests T1–T3) to A5 and A6.
- 2026-11-02 — v1.1. A2.9 revised to a fraction-order test (H-A2-06, H-A2-07), because the sceptre has no totals and the ring has no numerals. V8 partly resolved; A1.13 updated to match. Blinding breach on KN Zg 57/58 recorded in `research-notes.md`; blinded-check rule added to §0.4; register/hand caveat added to A4.6.
- 2026-11-04 — v1.2. Repo created (A1.1 mostly done); hypotheses are now one file each in `hypotheses/`. lineara.xyz pinned and found to contain the held-out sceptre records (excluded via `data/heldout.txt`). A1.3, A1.5, V2 updated.
- 2026-11-06 — A2 wrapped up on corpus-v0.1: Finding 002; H-A2-06 and H-A2-09 registered for future data; manual-check list for a human second reader. Remaining A2 items wait for new data (corpus-v1.0, *Anetaki II*, DAMOS) or literature (Montecchi).
- 2026-11-10 — v1.3. Project review with Marius. Revised order in §0.6. New analyses A8 (functional meaning without sound values) and A9 (claims audit, site comparison); new tasks A1.14, A1.15, A3.8, A3.9, A5.17, A5.18; V10; why and how for each in §0.7 and in the A8 and A9 sections. A5 split into Tier 1 (A5.17, brought forward) and Tier 2. Parked: A6, A7, A2.3, A2.4, A2.6, A2.7 (A2: Finding 002 showed the totals have no power and the value-set tests are no longer blind; A6/A7: high cost, nothing depends on them). A1.4–A1.9 completed the same day (PRs #25–#32).
- 2026-11-11 — A1.12 done: held-out split frozen (90 documents, not the estimated 114; §0.4, §0.6 budget and the A1.12 checkbox updated), corpus-v1.0 changelog written. No change to the order of work.
- 2026-11-11 — A1.14 done; A1.11 code done, report partial (two of three sources).
- 2026-11-11 — A8.1 draft gold set built (not frozen).
- 2026-11-12 — Process change, no change to tasks: Marius no longer merges; all PRs merge when CI is green, rule files are review-gated, and open items for him are kept in `docs/for-marius.md` (CLAUDE.md → Merging; research-notes 2026-11-12).
