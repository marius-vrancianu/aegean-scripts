# Corpus changelog

Results cite a corpus tag and a commit (`corpus-v1.0 @ abc1234`, CLAUDE.md). Newest release first.

## corpus-v1.0 — 2026-11-11 (A1.12)

The tag `corpus-v1.0` is created by Marius on the merge commit of the A1.12 pull request.

### Contents
| Component | Where | Pinned by |
|---|---|---|
| Canonical document list: 1,619 documents, 568 in the default analysis set | `data/processed/document-list/document-list.tsv` | SHA-256 in the release manifest |
| Witnesses, layers L0 and L1: 3,049 source readings (lineara.xyz 1,719; SigLA 827; Younger 503) | `data/processed/corpus-v1.0-pre/witnesses.jsonl`, not committed (licences); rebuilt by `python -m aegean.corpus.build_layers` | output hash in the release manifest |
| Held-out list: the Knossos sceptre (excluded at ingest) and the frozen split | `data/heldout.txt` | SHA-256 in the release manifest |
| Release manifest | `data/processed/corpus-v1.0/MANIFEST.json`, written by `python -m aegean.corpus.split` | — |

Sources: lineara.xyz @ `9c81beba`, SigLA @ `0c4ef69f`, Younger 2024 (Academia.edu PDFs; no Haghia Triada). Licences and provenance: `DATA_SOURCES.md`. Files derived from SigLA carry CC BY-NC-SA 4.0.

### Changes since corpus-v0.1
- Three sources instead of one, kept as separate witnesses and never merged (A1.4, A1.5, A1.7; `docs/schema.md`).
- One canonical document list keyed by GORILA siglum, with explicit inclusion rules (A1.6; `docs/inclusion-rules.md`).
- Layers L0 (sign IDs) and L1 (conventional Linear B values) for every witness (A1.8; `docs/layers.md`).
- Cross-source disagreement report (A1.9; `docs/reports/A1.9-source-disagreements.md`).
- **Held-out split frozen**: 90 of the 568 documents, stratified by site and support type, seed 20261111 (`docs/heldout-split.md`).
- **New loader** `aegean.corpus.load`: returns the training split by default; the held-out split only for a named, merged, confirmatory hypothesis.
- `data/heldout.txt` now has two kinds of line: `<source>:<id>` (excluded at ingest, as before) and `split:<document key>` (in the corpus, withheld by the loader).

### Limits
1. **The split is blind only for hypotheses registered after the freeze.** Before it, these steps processed every document, including the 90 now held out:
   - A1.6–A1.9: concordance, content tiers, schema validation, layer mapping and the disagreement report;
   - A2 on corpus-v0.1: H-A2-04, H-A2-07, H-A2-08 and the exploratory census (Finding 002);
   - Finding 001, which ran on the whole lineara.xyz word list.

   **Nothing from A2 can be confirmed on this split**, and no pattern noticed in that work counts as confirmed by a later held-out test of the same pattern. Hypotheses H-A2-06 and H-A2-09 remain tied to new data (the sceptre), not to this split.
2. **People and earlier sessions have read these texts.** The split hides the documents from code, not from memory: well-known tablets among the 90 are quoted in the literature and in this repository's own notes. A confirmatory hypothesis lists what its author already knows ("What I already know that could bias this").
3. **The split is 90 documents, 15.8% of the default analysis set, not 20%.** 88 strata with fewer than five documents (118 documents) stay wholly in training, because one or two documents cannot represent a stratum. Marius chose 20% of each remaining stratum over a fixed total of 114 (2026-11-11). Confirmatory power is correspondingly scarce (plan §0.6, held-out budget).
4. **A held-out result speaks for 22 strata at 12 sites.** The 45 sites that have only small strata, and rare supports at the larger sites, are never tested out of sample. Haghia Triada tablets are 28 of the 90.
5. **Stratification is by site and support type only.** Period, register, scribal hand, document length and number of sources were not balanced; by chance the two splits can differ on them. A1.11 reports those breakdowns for the training split only.
6. **Known corpus limits carry over** (A1.9): the Haghia Triada numerals and fractions rest on lineara.xyz alone; all three sources derive from GORILA, so their agreement is not accuracy; SigLA omits fractions on 57 documents; lineara.xyz has probable OVIS/CAP and site-label errors.
7. **The witnesses file was not rebuilt for this release.** Its hash is the one recorded by the A1.8/A1.9 build (`data/processed/corpus-v1.0-pre/MANIFEST.json`), and it keeps the `-pre` path, because the Younger PDFs cannot be fetched by script. The loader refuses a file whose hash differs. Moving it to `data/processed/corpus-v1.0/` needs one rebuild on a machine that has the PDFs.
8. **The loader's mapping from Younger witnesses to documents was not exercised on real data** in the freeze session, for the same reason. It was checked for all 2,546 lineara.xyz and SigLA witnesses (none unmatched). An unmatched witness raises an error; it is never treated as training data.
9. **The gate is a guard against mistakes, not a lock.** The held-out documents are in the corpus files and in the raw snapshots.
10. The sceptre (KN Zg 57, KN Zg 58) is a separate held-out item and is in no corpus file. Its blinding was partly compromised on 2026-11-02 (`research-notes.md`).

## corpus-v0.1 — 2026-11-04 (A1.0)
Provisional single-source release: lineara.xyz only, L0, sceptre excluded. Built by `python -m aegean.corpus.build`; manifest in `data/processed/corpus-v0.1/`. Used by A2 (Finding 002). Every result on it carries the single-source caveat.
