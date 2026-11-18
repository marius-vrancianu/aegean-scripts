"""Post hoc, not registered, decides nothing: Test 2 for the M2 pairs re-weighted by sign count AND class count.

Review of PR #60, N1: Test 2 re-weights the control to Linear A's sign-count distribution, but M2's hit rate
depends on the number of consonant classes, and the two inputs differ in classes per sign. This recomputes the
Test 2 difference with bins = (sign-count bin 2, 3, 4, 5+) × (class count 2, 3, 4, 5+), same pseudo-lexicons
(length-stratified, seed 20261114, 1,000), same leave-one-out p. Bins the control lacks are dropped.

  python experiments/A5.17/m2_class_reweighted_test2.py
Writes experiments/A5.17/results/M2-class-reweighted-test2.json (generated).
"""
import collections
import json
import statistics
from pathlib import Path

from aegean.benchmark import inputs, lexicons, tier1
from aegean.benchmark.m2 import M2
from aegean.corpus import load, resample

OUT = Path(__file__).resolve().parent / "results/M2-class-reweighted-test2.json"
PAIRS = {"H-A5-06": "hebrew-strong-verbs-dolgo", "H-A5-07": "english-verbs-dolgo", "H-A5-08": "turkish-verbs-dolgo"}


def joint_bin(m, g):
    return (tier1.length_bin(g), min(len(m.skeleton(g)), 5))


def rates(table, groups, m):
    by = collections.defaultdict(list)
    for g in set(groups):
        if g in table.index:
            by[joint_bin(m, g)].append(g)
    return {b: table.rates(gs) for b, gs in by.items()}


def main() -> None:
    m = M2()
    primary = resample.primary_reading(resample.group(load.witnesses()), tier1.SOURCE_ORDER)
    la = inputs.unique([g for _, g in inputs.linear_a_groups(primary)])
    control, _ = inputs.linear_b_control()
    out = {"kind": "post hoc, not registered, decides nothing", "seed_null": tier1.SEED_NULL}
    for h, lx in PAIRS.items():
        real = lexicons.REGISTRY[lx]()
        null = tier1.matched_lexicons(real, m, tier1.N_NULL, tier1.SEED_NULL, "stratified")
        t, ct = tier1.HitTable(m, la, real, null), tier1.HitTable(m, control, real, null)
        a, c = rates(t, la, m), rates(ct, control, m)
        used = sorted(b for b in a if b in c)
        w = {b: a[b][0] for b in used}
        tot = sum(w.values())
        k = len(null)
        la_real = sum(a[b][1] * w[b] for b in used) / tot
        la_null = [sum(a[b][2][i] * w[b] for b in used) / tot for i in range(k)]
        c_real = sum(c[b][1] * w[b] for b in used) / tot
        c_null = [sum(c[b][2][i] * w[b] for b in used) / tot for i in range(k)]
        mn, cm = statistics.fmean(la_null), statistics.fmean(c_null)
        d = (la_real - mn) - (c_real - cm)
        dn = [k / (k - 1) * ((la_null[i] - mn) - (c_null[i] - cm)) for i in range(k)]
        dropped = sum(a[b][0] for b in a if b not in c)
        out[h] = {"lexicon": lx, "bins_used": len(used), "linear_a_groups_in_used_bins": tot,
                  "linear_a_groups_dropped": dropped, "excess_linear_a": la_real - mn, "excess_control": c_real - cm,
                  "difference": d, "p": (1 + sum(x >= d for x in dn)) / (k + 1)}
        print(h, json.dumps({x: (round(v, 4) if isinstance(v, float) else v) for x, v in out[h].items()}))
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
