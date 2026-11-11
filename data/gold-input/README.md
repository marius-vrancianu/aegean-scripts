# Gold-set input (A8.1)

`literature-items.tsv` is the hand-written input to `python -m aegean.roles.gold`: sign-groups whose function is taken from the literature, not from this corpus. It is edited by hand; the output in `data/processed/gold/` is generated from it and from the witnesses.

Columns: the sign-group in conventional transliteration (L1, used only to find its L0 sign IDs through the uniform value table, `docs/layers.md`); role; referent; grade; the survey's confidence; sources; how the source was checked; a note.

Grades (set by Claude; a proposal, CLAUDE.md rule 5):
- **A**: the survey rates it near-certain or high, and the Linear B spelling is identical (place names) or the function is checked by arithmetic (KU-RO).
- **B**: medium to medium-high, or a name whose Linear B spelling differs, or a derived form.
- **C**: low, contested or resting on one search excerpt. Listed for the record; not used for scoring.

**Source check.** No primary source was read in the session that wrote this file. "survey" means the claim is in `docs/literature-survey-2026-10.md` §5; "search excerpt" means a search-engine excerpt of the cited page. Every row needs a check against the publication before the gold set is frozen.
