# aegean-scripts

Computational research on Linear A / Minoan and related Bronze Age Aegean and Anatolian scripts (Cretan hieroglyphs, Cypro-Minoan, Eteocretan, Lemnian, the pre-Greek substrate).

The aim is **falsifiable, reproducible results**, not decipherment: arithmetic constraints on the administrative tablets, affix and sign-value statistics tested against null models, and benchmarks that measure whether any language-matching method could work at Linear A's corpus size. Every method is validated on a known script (usually Linear B) first, and negative results are recorded alongside positive ones.

## Layout
| Path | Contents |
|---|---|
| `CLAUDE.md` | Rules for every contributor, human or agent. Read first. |
| `plans/` | Working plan with task IDs (A1–A9) |
| `hypotheses/` | One pre-registered file per hypothesis; immutable once merged |
| `findings/` | Results, positive and negative |
| `research-notes.md` | Append-only dated log |
| `DATA_SOURCES.md` | Every dataset: source, version, licence, conventions |
| `data/raw/` | Fetch scripts and hashes (data itself is fetched, not committed, unless licensed for redistribution) |
| `data/processed/` | Generated corpus files |
| `src/aegean/` | Python package |
| `experiments/` | Per-analysis configs, run scripts, outputs |
| `docs/` | Project brief, literature survey, guardrails |

## Getting started
```bash
pip install -e ".[dev]"
python data/raw/lineara.xyz/fetch.py   # downloads and verifies the pinned snapshot
pytest
```

## Status
Phase 2 (see `plans/phase2-analysis-plan.md`, order of work in §0.6):
- **Findings so far:** 001 (a published Semitic reading fails its null test) and 002 (what the arithmetic of totals can and cannot show; reviewed). No new positive result about Linear A yet.
- **Corpus:** `corpus-v1.0` is built from SigLA, lineara.xyz and Younger (1,619 documents listed, 568 in the default analysis set), with a cross-source disagreement report in `docs/reports/`. Changelog and limits: `docs/corpus-changelog.md`.
- **Held-out split:** 90 of the 568 documents are frozen as a confirmatory split (`docs/heldout-split.md`). Analyses load the corpus through `aegean.corpus.load`, which returns the training split unless a merged confirmatory hypothesis is named.
- **Next:** baseline statistics on the training split with the resampling harness, then the Linear A-only tests (claims audit, commodity association, abbreviation test).
- **Main goal:** a false-positive benchmark for decipherment methods (A5.17) and a functional role classifier validated on Linear B (A8.8).
- **Parked:** A6 (typology), A7 (palaeography) and the remaining A2 tasks.

## Licence
Not yet chosen; until a LICENSE file is added, all rights are reserved. Third-party data keeps its own terms (see `DATA_SOURCES.md`).
