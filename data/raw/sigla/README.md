# SigLA raw snapshot

**Licence:** CC BY-NC-SA 4.0. Dataset and drawings © Ester Salgarella & Simon Castellan,
*SigLA: The Signs of Linear A*, https://sigla.phis.me. Non-commercial use only; anything
derived from these files must carry the same licence (see `DATA_SOURCES.md`).

## Snapshot `0c4ef69f5de4/database.js`

| | |
|---|---|
| URL | https://sigla.phis.me/database.js |
| Size | 2,199,743 bytes |
| SHA-256 | `0c4ef69f5de4cc3d9382cca782c1cf47e2ca1be40696bcfc8e97514f9b0781dd` (`SHA256SUMS`) |
| Server headers | `Last-Modified: Tue, 27 Oct 2026 05:47:46 GMT`, `ETag: "3915148839"` |
| Fetched | 2026-11-10 by `curl`. Identical bytes were seen in a browser on 2026-11-06. |

`fetch.py` verifies the committed copy. `fetch.py --download` compares the live file with every pinned snapshot. If the live file has changed, add a new snapshot directory and a new `SHA256SUMS` line; never overwrite a pinned one.

**Held-out:** this snapshot contains no record of the held-out documents listed in `data/heldout.txt`. That was checked by document ID only. The only Knossos `Zg` document is `KN Zg <21>`, a different inscription. `aegean.corpus.sigla.load_documents` still filters every document through `data/heldout.txt`, matching normalised sigla across sources.

## Format

`database.js` defines two JS variables, `signs` and `data`. Each is a single-quoted JS string holding an OCaml string literal, and that literal's bytes are an OCaml `Marshal` value. `aegean.corpus.sigla` undoes both layers of quoting and decodes the value with `aegean.corpus.ocaml_marshal`. The decoder checks the marshal header's byte and object counts; both blobs pass.

SigLA does not document field names. The mapping below was established by comparing decoded values with the rendered static pages on 2026-11-10.
- **confirmed:** matches a rendered page; the page is cited in `tests/test_corpus_sigla.py`.
- **raw:** kept under a raw name because its meaning is not established.

### `data`: an OCaml `Map` from document ID to document (827 documents)

| Field | Content | Status |
|---|---|---|
| support | `Tablet` 452, `Nodule` 171, `Roundel` 164, … 21 values, spelling as given (`Libation Table` / `Libation table`, `Nodule?`) | confirmed |
| site | 23 sites | confirmed |
| dimensions_cm | `(h, w, d)`, optional | confirmed (HT 13, HT 22) |
| period | free text, optional: `LM IB` 655, `MM IIB` 34 …; also `''`, `n/a`, `unknown` | confirmed |
| corpus_link | link to the EFA *Études crétoises* page, optional | confirmed |
| seal | `(raw int, CMS number, motif, …)`, optional | CMS and motif confirmed (GO Wc 1a); first field raw |
| metadata_id | the ID inside the metadata record. It differs from the key in 7 documents, e.g. `KH 87` → `KH 97`, `PH Wa 52` → `PE Wa 52`, `KE Wc 2a` → `` `KE Wc 2a `` | kept for A1.9 |
| drawing_size | drawing size in px | confirmed (SVG viewBox) |

**Attestation** (5,184; each is one drawn sign, in SigLA's order):
| Field | Content | Status |
|---|---|---|
| sign | a sign record, or `[?]` (unidentified, 383) or `[unclassified]` (12) | confirmed |
| reading_sure | `sure-reading` / `unsure-reading` on the site; 44 unsure | confirmed |
| class | in a word → shown as "Syllabogram". Standalone → logogram 1,215, fraction 335, unknown 98, transaction 61, punctuation 7 | confirmed |
| class_uncertain | the class is shown with "?" | confirmed |
| word, index_in_word | position within a word | confirmed |
| erased | shown as "Erasure"; 104 | confirmed |
| hidden | 7 attestations are counted ("3 signs") but not drawn (HT 22 #3) | raw |
| pos_f2 | always 0 | raw |
| bbox | `(x, y, w, h)` in drawing px | confirmed |

**Word** (1,417): its attestation indices, plus left and right edge codes. The word view renders the codes like this:
- 0 → intact;
- 1 → `]-ka-ne` / `ru-mi-[`;
- 2 → `]ta-pi` / `a-pa-[?][`.

The site draws codes 1 and 2 differently but does not say what the difference means. A plausible reading is that 1 marks at least one lost sign beyond the break; this is **not verified** (medium-low confidence). The raw code is kept.

### `signs`: an OCaml `Map` keyed by number and by name (491 keys, 388 distinct signs)

Fields: series (`A`, `AB`, `AAF` = fractions, `AAP` = abstract signs `num`, `check-mark`, `word-divider`, `thumb-print`, `AAZ` = unnamed composites), number, variant, name (`OVIS`, `VIN`, `J`, `DD`, `num` …), reference attestation, conventional values, free-text notes, composition text, and the structured composition.

Composition operators, as written in the text field: `a + b` (ligature), `a | b`, `a || b`, and `a+{b}`. All four map exactly onto the structured field (`tests/test_corpus_sigla.py`). The difference between `|` and `||` is not described on the site.

**Conventional values are L1** (Linear B homomorph values such as `ka`). They stay in the sign table and never enter attestations (CLAUDE.md data rules).

## What this means for corpus-v1.0

- **No numeral values.** Numerals appear at most as the abstract punctuation sign `num` (`AAP800`), 7 times. SigLA cannot replace lineara.xyz as the numeral source for A2. It is an independent check on sign identities, fractions, word division and damage (A1.9).
- **Fractions.** The fraction signs are `AAF701–718`: A, B, D, E, F, H, J, K, L (with variants 2, 3, 4, 6), W, X, Ω, plus **DD (`AAF717`) and DDDD (`AAF718`) as single signs**. There is **no JE ligature sign**: J and E are separate attestations. lineara.xyz encodes JE as one ligature codepoint, so the two sources tokenise these differently, and the A1.7 schema has to reconcile them (Finding 002 review, M3).
- **Order.** The order of attestations is SigLA's index order. Whether this is reading order for stacked fraction signs is not established; the bounding boxes allow checking it (A1.9).
- **Damage** is recorded per word edge, not per sign. **Uncertainty** is recorded per sign (`reading_sure`). **Erasure** is recorded per sign. SigLA has no restoration field.
