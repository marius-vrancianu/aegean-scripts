# SigLA raw snapshot

**Licence:** CC BY-NC-SA 4.0. Dataset and drawings © Ester Salgarella & Simon Castellan,
*SigLA: The Signs of Linear A*, https://sigla.phis.me. Non-commercial use only; anything
derived from these files must carry the same licence (see `DATA_SOURCES.md`).

**Snapshot:** `database.js` from https://sigla.phis.me/database.js.
2,199,743 bytes, server `Last-Modified: Tue, 27 Oct 2026 05:47:46 GMT`, ETag `"3915148839"`.
SHA-256 in `SHA256SUMS`. `fetch.py` verifies the committed copy, and with `--download` it compares against the live file.

**Held-out:** no KN Zg 57/58 record in this snapshot. This was checked by document ID only, on 2026-11-06. The only `Zg` documents are HS Zg 1, HS Zg 11 and KY Zg 1. The ingest code still filters through `data/heldout.txt`.

## Format

`database.js` defines two JS variables, `signs` and `data`. Each is a single-quoted JS string holding an OCaml string literal, and the bytes of that literal are an OCaml `Marshal` value.

`aegean.corpus.sigla.load_raw` undoes both layers of quoting, then decodes the value with `aegean.corpus.ocaml_marshal`. The decoder checks the header's byte and object counts, and both blobs pass that check.

Record field names are not in the data. The layout below was inferred by comparing decoded values with the rendered site on 2026-11-06, mainly HT 13: its sign pages `index-N.html` and its word view.
- **confirmed:** checked against a rendered page.
- **inferred:** consistent across the data but not yet checked.

### `data`: one-field record holding a `Map` from document ID to document (827 documents)

| Document field | Content | Status |
|---|---|---|
| 0 | metadata record, 12 fields: see below | |
| 1 | document ID, e.g. `HT 13` | confirmed |
| 2 | drawing size in px, `(w, h)` | confirmed (SVG viewBox) |
| 3 | array of sign attestations, in SigLA's order | confirmed |
| 4 | array of words | confirmed |

Metadata: 0 support (`Tablet`, `Nodule`, `Roundel` …, with spelling variants); 1 ID; 2 site; 6 dimensions in cm, an option; 7 period, an option; 8 link to the EFA corpus, an option; 9 seal record, an option (`CMS` number and motif). These are confirmed for HT 13 and GO Wc 1. Fields 3–5, 10 and 11 are always 0.

Attestation, 6 fields:
| Field | Content | Status |
|---|---|---|
| 0 | index in the document | confirmed |
| 1 | back-reference to the document | confirmed |
| 2 | position record: `(location, f1, f2)`. `location` is either `InWord(index in word, word number)` or `Standalone(role)`, where role 0 = logogram, 1 = fraction, 2 = transaction sign (HT 13 #5, #9, #6). `f1` is 1 on some attestations and its meaning is not known. | location confirmed; f1/f2 open |
| 3 | sign: `(sign record, flag)`, or a constant 0 (383×) or 1 (12×). The constant 0 is probably an unidentified sign. The flag is 0 on 44 attestations and probably marks uncertain identification. | open |
| 4 | 0/1, with 1 on 7 attestations (HT 22, 33, 89, 94a; KH Wc 2047/2057/2065) | open |
| 5 | bounding box `(x, y, w, h)` in drawing px | confirmed |

Word, 4 fields: 0 index; 1 document back-reference; 2 `(left, right)` with values 0/1/2, probably the edge state; 3 list of attestations. Field 2 is **open**: ARKH 1a is broken and has many 2s.

### `signs`: a `Map` from `(number, variant option)` to sign record (491 entries)

The sign record has 10 fields:
- 0 series: `A` 267, `AB` 172, `AAF` 40 (fractions; `AAF707` = J, confirmed), `AAP` 8, `AAZ` 4;
- 1 number;
- 2 conventional values, as a list (e.g. `da`), **L1, not used for L0**;
- 3 reference attestation, e.g. `PH 31a/17`;
- 4 logogram name, an option (e.g. `OVIS`);
- 5 variant label, an option (`f`, `m`, `bis` …);
- 6 a boolean;
- 7 an option pair;
- 8 an option;
- 9 composition, an option: a variant (tags 1–4) over components. This is how ligatures and composite signs such as `A5xx` and `A3xx` are built, and how they are decomposed.

Fields 6–9 are not yet interpreted in detail.

## Consequences already visible

- **SigLA has no numerals.** It records signs, logograms, fractions and transaction signs, but not the numeral strokes, bars or circles. For example, HT 13 has 27 attestations and none of them is a numeral. SigLA therefore cannot replace lineara.xyz for A2 totals. It can serve as an independent check on sign identities, fractions and word division (A1.9).
- **The order of signs is SigLA's attestation order** plus in-word indices. Whether that is reading order for stacked fractions has to be checked (Finding 002 review, M3 and m2).
