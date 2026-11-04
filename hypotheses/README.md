# Hypotheses

One file per hypothesis, named by ID (`H-A2-01.md`), copied from `TEMPLATE.md`.

- A hypothesis is **pre-registered** when its file is merged into `main`. The merge commit is the timestamp of record.
- After that, the file is **immutable** (CI rejects edits, renames and deletions). To change a test, register a new hypothesis that references the old one, and count both.
- Outcomes go in `outcomes/H-A2-01.md`: result, statistic, null comparison, corpus version and commit, and a link to the finding.
- Dropped hypotheses still get an outcome file saying why. The total count of hypotheses tried per analysis must be recoverable from this folder.
