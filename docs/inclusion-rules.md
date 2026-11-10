# Inclusion rules for the canonical document list (A1.6)

**Status: PROPOSAL (2026-11-10).** The defaults below are mine (Claude) and await Marius's decision. Every rule is a parameter in `aegean.corpus.inclusion.Rules`, so changing one is a single argument, and the effect of each is counted here. Built by `python -m aegean.corpus.document_list` → `data/processed/document-list/`.

## What the list is

The list has **one row per document, keyed by GORILA siglum**, with the records of all three sources attached: lineara.xyz @ `9c81beba`, SigLA @ `0c4ef69f`, and Younger 2024, which has no Haghia Triada. Two outputs are kept apart:

- **`listed`**: in the canonical list at all. Only held-out documents are left out (and, optionally, unresolved IDs).
- **`analysis_default`**: used by analyses unless they state otherwise. Every exclusion is recorded with its rule number in `exclusion_reasons`.

Nothing is deleted. An analysis that wants single-sign nodules selects tier T2 explicitly.

## How documents are matched (`aegean.corpus.siglum`, `aegean.corpus.concordance`)

- **Sides belong to one document.** `HT 122a` and `HT 122b` are one row. Nodule faces α/β/γ and roundel edges (`latus`) are sides.
- **Angle brackets** (`KN Zb <27>`: reported but not seen by GORILA) are ignored for matching, because sources disagree on them. The `lost` flag keeps them.
- **Joins:** records sharing a numbered component form one document, because sources join fragments differently. SigLA has `KH Wc 2059+frr`, Younger `KH Wc 2059+2091+2092`. The key is the form most sources use; on a tie, the full join. Other forms are kept as `aliases`. There are 8 such documents.
- **Fragment letters** are separate GORILA documents: `HT 154A`…`N`, with lineara.xyz's `HT154ja` = SigLA's `HT 154Ja`.
- **Younger's shared entries** (`KH Wa 1003, 1004`, `KH Wa 1006-1008`) are attached to each document they name.
- **Irregular IDs** (Thera fragments, unnumbered Petras finds, museum numbers) are mapped by hand in `data/concordance/aliases.tsv`, each line with a confidence and a note. 3 IDs are **unresolved** and are not merged with anything.

## Counts (all documents, held-out excluded)

| | Documents |
|---|---|
| Total | **1,619** |
| In all three sources | 346 |
| lineara.xyz + SigLA | 301 |
| lineara.xyz + Younger | 157 |
| only lineara.xyz | 786 (mostly HT nodules) |
| only SigLA | 24 |
| only Younger | 5 |

## The rules

**R1 Scope (fixed).** Documents listed as Linear A by at least one of the three sources. All three are Linear A corpora; none of them is used to add documents of another script.

**R2 Held-out (fixed, not a proposal).** Documents in `data/heldout.txt` are excluded by every reader before parsing, matched across sources by normalised siglum. The frozen 20% split is added at A1.12.

**R3/R4 Content tier (PROPOSAL). This is the decision with by far the largest effect.** Each source's record is judged on its own, with sides summed, and the best source decides:

| Tier | Definition | Documents | Of which nodules |
|---|---|---|---|
| **T1 text** | ≥ 2 identified signs, or ≥ 1 sign and ≥ 1 numeral | **576** (194 HT, 382 other sites) | 35 |
| **T2 single sign** | exactly 1 identified sign, no numeral | **991** | 841 |
| **T3 no identified sign** | traces, unidentified signs or numerals only | **52** | 10 |

- *Proposed:* all tiers are **listed**; only **T1 enters analyses by default**.
- *Why:* a single sign on a nodule is usually a mark accompanying a seal impression, not a word. Younger (introduction §3a) likewise defines an inscription as two or more signs in conjunction. Treating 841 single-sign nodules as sign-groups would swamp A3/A4: their signs would be "words" of length 1 and would dominate the frequency counts.
- *Alternatives:* (a) include T2 in sign-frequency inventories (A1.11) but not in sequence analyses (A3/A4), which I'd also support; (b) include T2 everywhere; (c) drop T2/T3 from the list. I'd advise against (c), since nothing should be deleted.
- *Caveat:* the tier depends on how each source counts. SigLA records no numerals, and Younger counts a logogram cell as a sign. **The sources disagree on the tier of 67 documents**, which go into the A1.9 report.

**R5 Register (PROPOSAL).** This is taken from the GORILA series code, the same in every source:
- *administrative* (1,420): no series = tablet; `W*` = sealing documents (`Wa` nodule, `Wb` sealing, `Wc` roundel, other `W*`);
- *non-administrative* (199): `Z*` = inscriptions on other objects (`Za` stone vessel, `Zb` clay vessel, `Zc` inked, `Zd` graffito, `Ze` architecture, `Zf` metal, `Zg` stone object).

*Proposed:* both enter analyses by default, with the register a field that analyses select on. A2 already restricts itself to tablets.

**R6 Off-Crete documents (PROPOSAL).** 43 documents come from outside Crete (flag `off_crete`): Thera 25, Miletos 4, Mycenae 3, Kythera 2, Samothrace 4 (prefixes `SAM` and the older `SA`), Troy 2, and one each from Argos, Tel Haror and Tiryns. The prefix set was checked against the sources' site names. `SE` is Selakanos and `LACH` is Larani, both in Crete. *Proposed:* include. *Alternative:* exclude from analyses that assume a Cretan administration.

**R7 Single-source documents (PROPOSAL).** 815 documents are in one source only: 786 in lineara.xyz only, 24 in SigLA only, 5 in Younger only. Of these, 47 are T1 (lineara.xyz 39, SigLA 6, Younger 2). *Proposed:* include, flagged by `n_sources = 1`. *Alternative:* for T1 analyses, require two sources. That would cost 47 texts and all of SigLA's HT 154 fragments.

**R8 Joins (PROPOSAL).** The key is the join as most sources edit it, with the other forms as aliases (see "How documents are matched"). *Alternative:* split joins into components. That would contradict the editions and double-count shared lines.

**R9 Documents known only from reports (PROPOSAL).** These are GORILA's `<n>` sigla (16 documents: KN Zb <27>, <36>–<39>, KN Zg <21>, PH <29> …). Their texts come from earlier reports and cannot be checked against the object. *Proposed:* listed, **not in analyses by default** (flag `lost`). This excludes 6 that would otherwise be T1.

**R10 Unresolved IDs (PROPOSAL).** These are the 3 IDs in `aliases.tsv` marked `unresolved` (the unnumbered Palaikastro Zb items and "KN sceau"). *Proposed:* listed, **not in analyses** until a primary publication resolves them. 2 of the 3 are T1.

**Found while building the list (for A1.9, not resolved here):**
- **ARG Zg 1:** lineara.xyz gives the site as Arkhalkhori, while Younger places it at Argos (Nafplion Museum). It is treated as off-Crete.
- **SigLA's `SA We 3` / `SA We 4` vs `SAM We 4`:** Younger notes "SAM We 4 (formerly SA We 2)", so these may be renumberings of the same Samothrace nodules. They are kept apart.
- **Thera:** lineara.xyz and Younger's `THE fr.1-3` / `THE tab.4-6` versus SigLA's `THE 7-12` may be the same tablets under different numbers. They are kept apart.

**Not decided at A1.6 (left to A1.7):**
- **Period:** it is recorded per source; normalising it (`LM IB`, `LM I`, `MM III-LM I` …) is schema work.
- **Scribal hand:** SigLA has none; lineara.xyz and Younger have hands, from GORILA V.
- Uncertain-site flags (`site_uncertain`, 3 documents) are kept and not used for exclusion.

## Result with the proposed defaults

**1,619 listed; 568 in the default analysis set.** These are 576 T1 documents, less 6 lost and 2 unresolved. Exclusions by rule: T2 991, T3 52, R9 16, R10 3; a document can have more than one reason. See `data/processed/document-list/MANIFEST.json`.

## Decisions needed from Marius

1. **R3/R4:** T1 only by default (proposed), or T1 for sequence analyses and T1+T2 for sign inventories (alternative a)?
2. **R7:** accept single-source T1 documents (proposed), or require two sources?
3. **R9:** keep "lost" `<n>` documents out of analyses (proposed)?
4. Anything else in R5, R6, R8 or R10 you would set differently?
