# The frozen held-out split (A1.12)

Status: **frozen at corpus-v1.0.** Plan §0.4 fixes the policy; this file describes the procedure and how to use the split. Code: `aegean.corpus.split` (the draw), `aegean.corpus.load` (the gate), `aegean.corpus.heldout` (the list). The list itself is `data/heldout.txt`, a rule file: changes need Marius's merge.

## What was drawn

| | Documents | Strata |
|---|---|---|
| Default analysis set (`docs/inclusion-rules.md`) | 568 | 110 |
| In strata with fewer than five documents: wholly training | 118 | 88 |
| In strata that are split | 450 | 22 |
| **Held out** (20% of each split stratum) | **90** | 22 |
| Training | 478 | 110 |

The held-out split is 20.0% of the 450 documents it could be drawn from and **15.8% of the default analysis set**. Plan v1.3 §0.6 expected "about 114"; that figure did not allow for the small strata. Marius chose 20% per stratum over a fixed 114 on 2026-11-11 (the alternative was to draw 25.3% of each split stratum).

A stratum is a pair (site, support type), both as given in the document list. The unit is the document: all sides and all source readings (witnesses) of a held-out document are held out together.

## Procedure

1. Population: rows with `analysis_default = true` in `data/processed/document-list/document-list.tsv`.
2. A stratum with fewer than five documents stays wholly in training.
3. Every other stratum gives 20% of its documents, as a whole number: first the rounded-down share, then one more document each for the strata with the largest fractional parts, until the total is 20% of the 450 (ties go by stratum name). At this document list that equals ordinary rounding in every stratum.
4. Inside a stratum, documents are sorted by `sha256("<seed>|<document key>")`, and the first ones up to the quota are held out.
5. Seed: **20261111**, published in the pull request description before the first draw.

Step 4 uses a hash, not a random-number generator, so the result does not depend on a Python version, and one document can be checked by hand:

```
python -c "import hashlib; print(hashlib.sha256('20261111|HT 13'.encode()).hexdigest())"
```

No step reads a document's text. `python -m aegean.corpus.split --check` redraws and compares; `tests/test_split.py` does the same in CI, so the list cannot be changed by hand without CI failing.

## Quotas by stratum

Site codes: HT Haghia Triada, KH Khania, ZA Zakros, PH Phaistos, IO Iouktas, PK Palaikastro, SY Syme, THE Thera, KN Knossos, ARKH Arkhanes, MA Malia, PE Petras.

| Site | Support | Documents | Held out | Training |
|---|---|---|---|---|
| HT | tablet | 139 | 28 | 111 |
| KH | tablet | 85 | 17 | 68 |
| ZA | tablet | 27 | 5 | 22 |
| HT | nodule | 26 | 5 | 21 |
| PH | tablet | 23 | 5 | 18 |
| KH | roundel | 22 | 4 | 18 |
| HT | roundel | 18 | 4 | 14 |
| IO | stone_vessel | 14 | 3 | 11 |
| PK | stone_vessel | 14 | 3 | 11 |
| SY | stone_vessel | 10 | 2 | 8 |
| THE | clay_vessel | 10 | 2 | 8 |
| KN | clay_vessel | 8 | 2 | 6 |
| ARKH | tablet | 6 | 1 | 5 |
| KH | nodule | 6 | 1 | 5 |
| KN | tablet | 6 | 1 | 5 |
| PH | roundel | 6 | 1 | 5 |
| HT | clay_vessel | 5 | 1 | 4 |
| KN | architecture | 5 | 1 | 4 |
| KN | roundel | 5 | 1 | 4 |
| MA | tablet | 5 | 1 | 4 |
| PE | tablet | 5 | 1 | 4 |
| THE | tablet | 5 | 1 | 4 |
| **Total** | | **450** | **90** | **360** |

## Strata kept wholly in training (88 strata, 118 documents)

Site code, then support type and number of documents:

**AP** stone_vessel 2; **AR** metal_object 2; **ARG** stone_object 1; **ARKH** inked 1, metal_object 1; **ARM** stone_object 1; **CR** metal_object 1, stone_object 2; **DRA** stone_object 1; **FO** inked 1; **GO** roundel 2, tablet 1; **HS** stone_object 1; **HT** graffito 2, metal_object 1, sealing 1; **HTW** tablet 1; **IN** clay_vessel 1; **IO** clay_vessel 1; **KA** metal_object 1; **KAM** clay_vessel 1; **KAN** stone_vessel 1; **KE** clay_vessel 2, roundel 1, tablet 1; **KH** inked 1; **KN** inked 2, metal_object 2, sealing 1, stone_object 1, stone_vessel 4; **KO** metal_object 1, stone_vessel 1; **KY** stone_object 1, stone_vessel 1; **LA** clay_vessel 1; **LACH** stone_vessel 1; **MA** architecture 1, clay_vessel 1; **MI** clay_vessel 2, tablet 1; **MIL** clay_vessel 4; **MO** metal_object 1; **NE** stone_vessel 1; **PA** tablet 1; **PE** clay_vessel 2, inked 1, other_sealing 1, stone_object 2; **PH** clay_vessel 3, nodule 1, other_sealing 1; **PK** clay_vessel 4, inked 1, stone_object 1, tablet 2; **PL** metal_object 1; **PO** inked 1; **POR** metal_object 1; **PR** stone_vessel 1; **PS** stone_vessel 1; **PSI** stone_vessel 1; **PYR** clay_vessel 1, roundel 1, tablet 1; **SAM** nodule 1, other_sealing 1; **SE** metal_object 1; **SI** stone_object 1; **SK** clay_vessel 1; **SKO** inked 1; **SY** clay_vessel 1; **TEL** clay_vessel 1; **THE** stone_object 3; **TI** clay_vessel 1; **TL** stone_vessel 1; **TRA** clay_vessel 1; **TRO** stone_object 2; **TRY** clay_vessel 1; **TY** clay_vessel 1, stone_object 1, tablet 2; **VRY** clay_vessel 2, stone_vessel 1; **ZA** clay_vessel 2, roundel 1, stone_object 2; **ZO** tablet 1.

The machine-readable table is `split.by_stratum` in `data/processed/corpus-v1.0/MANIFEST.json`.

## Using the corpus

```python
from aegean.corpus import load
docs = load.documents()      # training split, default analysis set: 478 documents
ws = load.witnesses()        # their witnesses, each with a doc_key field
```

Reading held-out documents needs the ID of a frozen confirmatory hypothesis:

```python
ws = load.witnesses(split="heldout", heldout_for="H-A3-01")   # or split="all"
```

The loader accepts the ID only if `hypotheses/<ID>.md` exists, is identical to the version on `origin/main` (merged, so pre-registered and immutable), and contains the line `- **Type:** confirmatory` (CLAUDE.md rule 10). Otherwise it raises `HeldoutAccessError`. Each release prints a notice to stderr.

Two limits of the gate:
- It stops mistakes, not intent. The held-out documents are inside `witnesses.jsonl` and the raw snapshots; code that opens those files directly bypasses the gate. Analyses must go through `aegean.corpus.load`.
- `hypotheses/TEMPLATE.md` has no `Type` line yet. Adding one is a change under `hypotheses/` (review-gated), so it is left to its own PR. Until then a confirmatory hypothesis adds the line itself.

## What the split can and cannot confirm

See `docs/corpus-changelog.md`, "Limits". In short: it is blind only for hypotheses registered after the freeze; nothing from A2 can be confirmed on it; and it says nothing about the 88 small strata.
