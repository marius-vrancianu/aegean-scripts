# Project brief: Protohistoric Mediterranean Linguistic Analysis

## Goal
Gain a better understanding of prehistoric, protohistoric and early classical Mediterranean languages and writing systems, especially Minoan and Linear A. The aim is falsifiable, reproducible results with stated confidence levels, obtained by any creative means: brute-force programming, statistical analysis, AI-assisted pattern finding. No genuine knowledge gain is too small, as long as it holds water. Full decipherment is not the expected outcome. Narrower results count: sign-value consistency tests, morphological segmentation, scribal-hand clustering, controlled tests of language-family hypotheses, and well-documented negative results.

## Scope
Primary: Linear A / Minoan.
Also in scope: Cretan hieroglyphs, Eteocretan, Eteocypriot, Cypro-Minoan, the Cypriote syllabary, the pre-Greek substrate, Lemnian/Tyrsenian, and any Semitic, pre-Indo-European or Indo-European influence detectable around the Aegean and Anatolian Bronze Age.

## Context
- Long-term hobby project (10+ years), worked on irregularly with no fixed schedule. Each session should leave the work resumable.
- Marius works from secondary literature and does not read Linear B, Greek, Semitic or Anatolian languages (open to learning some). Explain philological concepts, conventions and notation when they come up. Do not assume background knowledge.
- No institutional literature access for now. Prefer open sources and flag when a key source is paywalled.
- Build on existing digital corpora first. Record the source, version, licence and transcription conventions of every dataset used.
- Compute is limited to one personal PC plus free cloud resources (Google Colab, GitHub). Design methods to fit.
- Phase 1 (exploratory survey) is complete: `docs/literature-survey-2026-10.md`. Phase 2 plan: `plans/phase2-analysis-plan.md`.

## Methodological rules
1. Null models: every claimed pattern is tested against an explicit null, such as shuffled corpora or random pseudo-languages, before it counts as a finding.
2. Multiple comparisons: correct for them. Report how many hypotheses were tried, not just the ones that worked.
3. Pre-registration: log hypotheses and the planned tests before testing them, especially before running on held-out data.
4. Validation on known scripts: any decipherment-type or pattern-finding method is first validated on Linear B or another known script, to show it recovers the known answer.
5. AI output is not evidence: any reading, sign value, etymology or parallel proposed by an LLM, including Claude, is a hypothesis to test.
6. Confidence and sources: claims carry explicit confidence levels and citations. Distinguish consensus, mainstream-but-contested, and fringe positions.
7. Negative results are results: record them with the same care as positive ones.

## Infrastructure
This repository is the single source of truth: versioned data (or pinned fetch scripts where licences forbid redistribution), code, pre-registered hypotheses, results including negative ones, and a running research-notes file. Ten-year projects die from lost context, not lost compute.

## Publication
Deferred. Produce work that would survive peer review: reproducible code, clean data provenance, documented methods. An academic co-author can be sought once there is something worth publishing.
