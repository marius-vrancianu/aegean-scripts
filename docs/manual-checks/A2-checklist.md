# Manual check list for A2 (for Marius, or any second reader)

**Purpose:** a human second reading of the tablets that matter most to the A2 results. Each check takes 2–5 minutes, and you don't need to know Linear A. Numeral basics are in the box below.

> **Reading numerals:**
> - **Units** are short vertical strokes, **tens** are short horizontal strokes (or dots), **hundreds** are circles, and **thousands** are circles with rays.
> - Count every stroke in a cluster; the way the strokes are stacked means nothing.
> - **KU-RO** ("total") looks roughly like `ㄱ +`.
> - **Stippling** (fine dots) marks a damaged surface, and **dashed lines** mark cracks or breaks.

**Drawings:** `https://raw.githubusercontent.com/mwenge/lineara.xyz/9c81beba669a4ffec3f5b29d4e7748d02c060eff/images/<ID>-Facsimile.jpg`. Replace `<ID>` with the tablet ID, e.g. `HT9b`.

**Younger's transliterations,** which mark restorations with brackets: https://www.people.ku.edu/~jyounger/LinearA/HTtexts.html (Hagia Triada texts). Open it in your browser. Automated access is blocked for Claude.

## What to record per tablet
In `experiments/A2/gorila-checks/checks-<date>-marius.csv`, with the same columns as `checks-2026-11-05.csv`:
1. **The KU-RO number.** Is every stroke clearly visible? Answer `yes`, or `partly` (something could be hidden or extra), or `no`.
2. **The entry numbers above the KU-RO.** Are all their strokes clearly visible? Answer `yes`, `partly` or `no`.
3. **Could entries be missing?** Is there a broken edge, a missing corner or a lost line where entries would have been? Answer `yes` (the entry area is complete), `no` or `unclear`.
4. **Optional, in Younger:** is any number of this tablet in square brackets `[ ]`, i.e. restored by an editor?

If you can, record your answers **before** looking at Claude's row for the same tablet. The more cautious of the two judgements is used.

## Priority 1: "damaged" but the sums are exact (decides how strong the census result is)
| Tablet | KU-RO | Claude's concern |
|---|---|---|
| HT 9b | 24 | entries inside a stippled area |
| HT 11b | 180 | Claude could not find the 180 in the drawing |
| HT 25b | 52 (lower KU-RO) | entries 28 and 24 partly in stipple |
| HT 85a | 66 | stippled band touches the total; **the edition also marks the 66 as damaged** |
| HT 89 | 87 | crack through the KU-RO line |
| HT 94b | 5 | stippled band beside the units |
| HT 104 | 95 | lines 3–4 in a stippled band |

## Priority 2: near misses (off by one stroke)
| Tablet | KU-RO | Entries sum | Question |
|---|---|---|---|
| HT 119 | 160 | 159 | is there a unit stroke more somewhere, or one fewer ten? |
| HT 94a | 110 | 111 | crack near the entries of lines 1–2 |
| HT 102 | 1060 | 1070 | is the thousand sign really there? one entry is "33]" |
| HT 122b | PO-TO-KU-RO 97 | KU-RO 31 + 65 = 96 | 96 or 97? (you already read "97, maybe 96") |

## Priority 3: KI-RO tablets (needed before any KI-RO claim)
These have not been checked by anyone yet. The list is the KI-RO rows in `experiments/A2/exploratory/census-all.csv`.

## Priority 4: order of stacked fraction signs (review of Finding 002, m2)
Corazza et al. say larger fractions are written to the left of or **above** smaller ones. When two signs are stacked, the edition has to decide which comes first in the linear transcription. For each tablet below, look at the drawing and note whether the fraction signs sit **side by side** or **stacked**. If they are stacked, note which one is on top.

| Tablet | Pair in corpus-v0.1 |
|---|---|
| HT 16 | E F |
| HT 8b | E F |
| KH 11 | K L2 |
| KH 5 | J B |
| HT 33 | E L2 |
| ZA 8 | E J (the one reversal) |
