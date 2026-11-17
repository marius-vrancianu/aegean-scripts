"""Descriptive check registered in hypotheses/H-A5-02.md ("What I already know", N6 of its review).

Both Tier 1 tests for M1 × english-verbs, recomputed with every two-letter form removed, after expansion,
from the real lexicon and from each of the 1,000 matched pseudo-lexicons alike. Same seeds, inputs and
code paths as the registered run. It decides nothing.

  python experiments/A5.17/h_a5_02_no_two_letter.py

Writes experiments/A5.17/results/H-A5-02-no-two-letter.json (generated).
"""
import json
import statistics
import sys
from pathlib import Path

from aegean.benchmark import inputs, lexicons, tier1
from aegean.benchmark.m1 import M1
from aegean.corpus import load, resample

OUT = Path(__file__).resolve().parent / "results/H-A5-02-no-two-letter.json"


class M1WithoutTwoLetterForms(M1):
    """M1 whose prepared lexicon drops every form of two letters (after the interchanges)."""
    name = "M1-no-2"

    def prepare(self, lexicon):
        return frozenset(f for f in super().prepare(lexicon) if len(f) != 2)


def main() -> int:
    base, cut = M1(), M1WithoutTwoLetterForms()
    real = lexicons.english_verbs()
    null = tier1.matched_lexicons(real, base, tier1.N_NULL, tier1.SEED_NULL)  # drawn exactly as in the run
    ws = load.witnesses()
    primary = resample.primary_reading(resample.group(ws), tier1.SOURCE_ORDER)
    la = inputs.unique([g for _, g in inputs.linear_a_groups(primary)])
    control, _ = inputs.linear_b_control()
    out = {}
    for name, m in (("as_registered", base), ("without_two_letter_forms", cut)):
        table, ctable = tier1.HitTable(m, la, real, null), tier1.HitTable(m, control, real, null)
        c1, cc = table.compare(la), ctable.compare(control)
        d = tier1.difference_test(table, la, tier1.Control(ctable, control))
        sizes = [len(m.prepare(l)) for l in null]
        out[name] = {"lexicon_forms_real": len(m.prepare(real)), "lexicon_forms_null_mean": statistics.fmean(sizes),
                     "lexicon_forms_null_low": sorted(sizes)[25], "lexicon_forms_null_high": sorted(sizes)[974],
                     "lexicon_forms_null_min": min(sizes),
                     "linear_a": {k: c1[k] for k in ("n", "real", "false_positive_rate", "excess", "p")},
                     "control": {k: cc[k] for k in ("n", "real", "false_positive_rate", "excess", "p")},
                     "test2": {k: d[k] for k in ("excess_linear_a", "excess_control", "difference", "p")}}
    OUT.write_text(json.dumps({"hypothesis": "H-A5-02", "kind": "descriptive, decides nothing",
                               "seed_null": tier1.SEED_NULL, **out}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for k, v in out.items():
        print(k, json.dumps(v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
