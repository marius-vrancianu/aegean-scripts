# Layers L0 and L1 (A1.8)

Code: `aegean.corpus.layers`; build: `python -m aegean.corpus.build_layers`, which writes `data/processed/corpus-v1.0-pre/` (`witnesses.jsonl`, gitignored; `MANIFEST.json`, committed). Schema: `docs/schema.md` (v0.2 adds `Token.l1`). L2 comes from A5.

## L0: sign identities

- **lineara.xyz:** from Unicode codepoints (A1.7). All 6,695 tokens have a sign ID.
- **SigLA:** from SigLA's sign IDs (A1.7). 4,789 of 5,184 tokens have one; the other 395 are unidentified (`[?]`, `[unclassified]`).
- **Younger:** prints values (L1), so this module maps them back to sign IDs. **2,709 of 3,035 tokens are mapped; 54 are unidentified.** About 270 remain unmapped: stray notation (`vest.`, `a:`, numerals inside inscriptions), partly broken ligatures (`]*303+[ ]`), and ligatures written out with no number (`*301+*311`).

### The Younger map, in order of priority

| Rule | Example | Source of the mapping |
|---|---|---|
| sign number | `*301` → A301, `*411VASb` → A411b | the value *is* the number |
| Younger's brace number | `GRA+PA {*574}` → A574 | Younger's own text |
| syllabic value | `KU` → AB081 | **Unicode Linear B** syllable names (Unicode 15.1), which encode Bennett number + value |
| values Unicode lacks | `PA3` → AB056, `PU3` → A314, `ZU` → AB079, `AI` → AB043 | `YOUNGER_EXTRA`, each with its evidence (below) |
| logogram label | `VINa` → AB131a, `OVISf` → AB021f, `OLE` → A302 | **SigLA's sign-table names** |
| value + sex variant | `QIf` → AB021f | value table + GORILA f/m variants |
| fraction letter | `J` → A707 | A1.7 fraction table |
| written-out ligature | `*301+*311` → SigLA composite with the same composition text, else components only | SigLA sign table |

**Evidence for the four extra values:**
- `*56 = PA3` and `*314 = PU3`: Younger's introduction, section "Phonetic values of the signs".
- `ZU = *79`: Younger writes the same HT 13 word both KU-\*79-NI and KU-ZU-NI. SigLA's HT 13 has AB079 in that position.
- `AI = AB043`: SigLA's sign table (`ai`); Unicode writes A3.

None of these comes from my (Claude's) own knowledge (CLAUDE.md rule 5).

### Validation against SigLA

On the **335 documents** that Younger and SigLA share, Younger's mapped word signs were aligned with SigLA's (difflib on base sign IDs; only equal-length blocks scored).

**1,125 signs align, and 1,112 (98.8%) agree.** Every extra value agrees each time it aligns:

| Value | SigLA sign | Agreement |
|---|---|---|
| PA3 | AB056 | 8/8 |
| ZU | AB079 | 8/8 |
| PU3 | A314 | 4/4 |
| AI | AB043 | 1/1 |

The remaining 13 disagreements are reading differences between the editions, or alignment noise. They are left for A1.9; one example is Younger's SO where SigLA has A363 or A364.

*What this shows:* the value map is consistent with an independent edition. It is not a check against the tablets. Confidence in the map: high.

## L1: one conventional value per sign, assigned uniformly

`Token.l1` is computed **from the L0 sign ID alone**, the same way for every source:

- **AB signs:** the **Unicode Linear B syllable value** (DA, RO, PA … PU2, TA2, RA2, RA3, RO2, A2, A3, NWA, PTE, DWE, DWO, TWE, TWO).
- **Signs Unicode leaves without a value** (Linear B "symbols" B018, B019, B022, B034, B047, B049, B056, B063, B064, B079, B082, B083, B086, B089) stay as numbers: `*22`, `*34`, `*56`, `*79` … This is deliberately conservative: values like pa3 for *56 or zu for *79 are conventions, not Unicode readings. Switching them on would be a change to `l1_of`, logged as a decision.
- **Linear A-only signs** stay as numbers: `*301`, `*131a`, `*411b` (the plan's L1 definition: "*301 kept as *301").
- **Fractions** keep their letter names (J, E, L2 …); fraction ligatures join them (JE, DD).
- **SigLA's abstract signs** (`SigLA:AAP800` …) have no L1.

`Token.l1_value` keeps the value **as the source printed it** (Younger only). Where it differs from `l1`, the difference is data for A1.9, not corrected here.

### Why Unicode Linear B, and not SigLA's values

SigLA gives values for only **62 signs**, and it lacks 16 standard Linear B values (DO, JO, MO, NO, QO, SO, WE, WO, A2 …). Two of its entries differ from Unicode:
- `AB043 ai` against Unicode `A3`: the same value, spelled differently;
- **`AB072 ko` against Unicode `PE`:** SigLA also gives ko to AB070, so this looks like a SigLA error. It goes to A1.9.

## Corrections made while building the layers

- **SigLA sign values:** the A1.4 reader read the subscript of a value as a second value (`AB29: pu, 2`). It is `pu2`. The reader is fixed; no earlier result used these values.
- **Canonical series follows the number** (Bennett: AB below 300, A from 301) for all inputs. SigLA writes OLE as `AB302`, which is now `A302`; Unicode's `A028B` was already handled in A1.7.
