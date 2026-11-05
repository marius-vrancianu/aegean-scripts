# GORILA checks for H-A2-08 (step 1)

- `checks-2026-11-05.csv` has one row per KU-RO and PO-TO-KU-RO occurrence in corpus-v0.1 (39 rows, 35 sides).
- **Checked by Claude on 2026-11-05**, counting strokes, against the GORILA facsimiles in the lineara.xyz images folder at commit 9c81beba. Images were viewed in scratch space and not committed. Rule 5 applies: these are checks, not readings with authority.
- **Committed before any sum was computed**, as H-A2-08 requires.

## Standard used
- **Intact `yes`:** every stroke of the quantity is clear, and no break, crack or stippling touches it.
- **Intact `partly`:** a break, crack or stippling touches the quantity or could hide a stroke, **or** Claude could not confidently match the reading to the drawing.
- **Intact `no`:** the quantity is not visible.

When in doubt, the judgement is `partly`. This is the cautious choice the hypothesis file asks for.

## Deviations from H-A2-08, recorded openly
1. **Scope entries are judged as a group, not one by one.** H-A2-08 asks for a facsimile reading per entry. On most tablets, lineara's entry segmentation does not map one-to-one onto the physical lines, so entries were judged together (`scope_entries_intact`), with specifics in `notes`. The total is still recorded individually.
2. **The comparison exposed every number to Claude.** That is unavoidable when comparing readings with drawings. No sum was computed or estimated before this file was committed.
3. **Category 1 and 2 rows** (no total; fraction signs present) were viewed, but their numerals were not always transcribed, because the census category does not depend on them.

A second check by Marius on any subset is welcome. Where he and Claude disagree, the more cautious judgement is used (H-A2-08, step 1).
