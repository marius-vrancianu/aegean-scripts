# Finding 001 — Ya Diktu null test

- `original/` holds the scripts exactly as run on 2026-10-28. Do not edit them; they are the record.
- `reproduce.py` runs them against pinned inputs in a temporary HOME, because the scripts hard-code `~/yadiktu/`.

```bash
python experiments/finding-001/reproduce.py                    # original run
python experiments/finding-001/reproduce.py --exclude-heldout  # with data/heldout.txt applied
```

Expected output: `findings/001-yadiktu-null-test.md` (Results table, and the addendum of 2026-11-04). Runtime is about a minute on a PC.

The reusable benchmark version of this matcher (method M1) is to be written under `src/aegean/benchmark/` in A5.12. It should be built from these scripts, not edited into them.
