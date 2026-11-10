# Corpus schema (A1.7), version 0.2

v0.2 (A1.8) adds `Token.l1`, the uniform L1 value computed from `sign_id` (see `docs/layers.md`). `Token.l1_value` remains the value as the source printed it.

Code: `aegean.corpus.schema` (records, sign IDs, `validate`) and `aegean.corpus.witnesses` (one adapter per source). The document list and its inclusion rules are in `docs/inclusion-rules.md` (A1.6). Building the layers and the corpus-v1.0 files is A1.8.

## Structure

```
Document (GORILA siglum; data/processed/document-list/, A1.6)
 └─ Witness        one source's reading of one document (or of one side, where the source splits sides)
     └─ Line       a line as the source has it (physical side.line, entry line, or none)
         └─ Item   a sign-group (word), logogram, numeral, fraction, divider, lacuna, ruling, vacat ...
             └─ Token   one sign
```

**A witness is never merged with another.** Comparing witnesses is A1.9; choosing a reading per document is A1.8. Every mark therefore has exactly one source: the witness it belongs to.

## Three conventions

1. **None vs False.** A mark that the source does not record is `None`; `False` (or `""` for breaks) means the source records it as absent. Example: lineara.xyz records no per-sign doubt, so its `doubtful` is always `None`. Absence there is not evidence.
2. **Layers** (plan §0.1).
   - `Token.sign_id` is **L0**: the GORILA/Bennett sign number.
   - `Token.l1_value` is a conventional (Linear B) value, filled **only where the source itself gives one**, which here means Younger.
   - No adapter fills `sign_id` from a value. Younger's values are mapped to sign IDs in A1.8, except `*nnn` values, which are sign numbers and map directly.
   - Value-converted fields such as lineara.xyz's `transliteratedWords` / `translatedWords` are never parsed for content (CLAUDE.md). The only thing read from them is the existing damage-bracket flag (`translit_bracket`).
3. **Order is the source's.** Items and tokens keep the source's linear order. For stacked fraction signs this is an editorial linearisation (Finding 002 review, M3). `Token.stacked` is `None` in all three sources, because none records stacking. SigLA's bounding boxes could recover it (A1.9).

## Canonical sign IDs

The format is `AB` or `A`, then a 3-digit number, then the GORILA variant suffix: `AB081`, `AB131a`, `AB021f`, `A301`, `A309a`, `A506bis`, `A709-2`.

- **AB below 300, A from 301.** This follows Bennett's numbering. Unicode names some variants of AB signs in the A series (`A028B`, `A120B`, `A131C`); they are normalised to `AB028b` etc. This is a normalisation choice, medium-high confidence that it matches GORILA.
- **Fractions** are `A701`–`A718`, with letter names A, B, D, E, F, H, J, K, L, L2, L3, L4, L6, W, X, Y, Ω.
- **Ligatures of fractions keep both forms:** `sign_id` is the single sign as the source writes it, and `components` lists its parts, in the order the sign name gives them. This answers the Finding 002 review, M3: lineara.xyz encodes JE and DD as single codepoints.

  | sign_id | letters | components | in sources |
  |---|---|---|---|
  | A714 | ABB | A701 A702 A702 | Unicode |
  | A715 | BB | A702 A702 | Unicode |
  | A717 | DD | A703 A703 | lineara.xyz, SigLA |
  | A718 | DDDD | A703 ×4 | SigLA only (not in Unicode) |
  | A726 | EYYY | A704 A712 ×3 | Unicode |
  | A732 | JE | A707 A704 | lineara.xyz |

  Composite signs (`A5xx`, `A6xx`) carry the components SigLA's sign table gives them.
- **`base_id()`** drops the variant (`AB131a` → `AB131`), for comparing a source that distinguishes variants with one that does not.
- **The Unicode codepoint** is an attribute (`unicode_codepoint()`), not the ID. 326 of SigLA's 388 signs have one. The other 62 are composites, vessel-sign variants, DDDD, and base forms that Unicode encodes only as variants.
- **SigLA's abstract signs** (`AAP800` num, `AAP801` check-mark, `AAP802` word-divider, `AAP803` thumb-print) and its unnamed composites (`AAZ…`) have no GORILA number. They are `SigLA:AAP800` etc., so they can never collide with one.

## Fields

**Witness:** source, source_id, source_version (snapshot hash prefix), side, layer (`L0` or `L0+L1`), lines, period and scribe as the source gives them, notes (the source's commentary; not data), flags.

**Line:**
- `index`;
- `ref` (`a.1`, `.3-4`) or None;
- `ref_kind`: `physical` (Younger's side.line, after GORILA), `entry` (lineara.xyz's entry lines, which do not always follow the tablet's lines) or `none` (SigLA has no lines);
- `ruling_before`.

**Item:**
- `kind`: word, logogram, numeral, fraction, transaction, unknown, punctuation, divider, lacuna, ruling, vacat, other or mixed;
- `tokens`;
- `numeral_value`: an exact integer, the additive value of the numeral group;
- `divider_after`;
- `left_break`, `right_break`: the group's breaks, as the source marks them;
- `lacuna_estimate`: Younger's `[ • • • ]`;
- `raw`, `flags`.

**Token:**
- `written_as`: the source's own encoding;
- `sign_id`, `role`, `components`, `unidentified`;
- `l1_value` (as printed by the source) and `l1` (uniform, from `sign_id`; A1.8);
- `doubtful`, `erased`, **`restored`** and **`conjectural`**, kept as separate fields;
- `break_before`, `break_after`, `stacked`, `bbox`, `flags`.

## Field coverage by source

What each source records. "None" means the field is always `None` for that source.

| Field | lineara.xyz @ 9c81beba | SigLA @ 0c4ef69f | Younger 2024 (non-HT) |
|---|---|---|---|
| Lines | entry lines (`entry`) | none | physical side.line (`physical`) |
| Sides | separate records (`HT122a`) | separate records (`HT 122a`, α/β/γ, latus) | inside one entry (`a.1`, `b.2`) |
| `sign_id` | Unicode codepoints → canonical | SigLA IDs → canonical | from `*nnn` and `{*nnn}` only; values → A1.8 |
| `role` | None, except numerals and fractions | full (syllabogram, logogram, fraction, transaction, unknown, punctuation) | from the column (statement, logogram, number, fraction) |
| Numerals | values | **none** (at most an abstract `num`, 7×) | values |
| Fractions | letters → A70x; JE, DD as ligatures | A701–A718; DD, DDDD single signs, no JE | letters → A70x, separate (no ligatures) |
| `doubtful` | None | `unsure-reading` (44) | underline (465 tokens) |
| Breaks | U+1076B at a group edge, or a bracket in the transliteration; **incomplete**, so an unmarked edge is None | word-edge codes 0/1/2 → `""`/`]-`/`]` | `]`, `]-`, `[`, `-[` per sign |
| `erased` | None | per sign (104) | `[[ ]]` (4) |
| `restored` | None (restorations not marked) | None | `< >` (2) |
| `conjectural` | None | None | green: only in reconstructions, which are never in witnesses |
| Unidentified signs | None | `[?]` (383), `[unclassified]` (12) | `-•-`, `[•]` (53) |
| Rulings | `—` (U+2014) items (56) | none | ruled lines (27) |
| `stacked` | None | None (bounding boxes could recover it) | None |
| Period | `context` field | `period` field | not parsed (in the header text) |
| Scribe | `scribe` field | none | magenta annotation ("ZA Scribe 2") |

**Damage vs restoration.** These are separate fields, each from its own source:
- a break is `left_break` / `right_break` (group) or `break_before` / `break_after` (sign);
- a restoration is `restored` (Younger `< >`); Younger's own fills are `conjectural`.

No source here marks restorations comprehensively. A1.9 must not read "not restored" from a `None`.

## Validation

`schema.validate(witness)` checks item kinds, roles, canonical sign IDs, numerals with values, and that unidentified tokens have no `sign_id`. All 3,049 witnesses validate with no errors:

| Source | Witnesses | Tokens |
|---|---|---|
| lineara.xyz | 1,719 | 6,695 |
| SigLA | 827 | 5,184 |
| Younger | 503 | 3,036 |

## Known gaps (for A1.8 and A1.9)

- Younger's syllabic values (KU, RA2 …) and logogram labels (OVIS, VINa …) are not yet mapped to sign IDs (A1.8). 2,474 of his 3,036 tokens wait for that table.
- Three Younger fraction cells hold non-fraction text, a layout leftover: one `FIC` is flagged `unknown_fraction_letter`; the `[•]` and `vest.` cases are handled.
- lineara.xyz's entry lines are not physical lines. Aligning lines across sources is A1.9.
- Sides: lineara.xyz and SigLA split them, while Younger does not. Witness-to-document grouping comes from the A1.6 concordance.
