"""How M2's threshold (normalised edit distance 1/4) was chosen: committed after the fact (review of PR #60, N5).

Uniform random strings of Linear B values (not Linear A, not the control): 300 of two signs, 400 of three,
200 of four, 100 of five, from random.Random(99); real lexicons and 20 length-stratified pseudo-lexicons
(random.Random(0) ... random.Random(19)) at thresholds 0, 1/4 and 1/3. This reproduces the figures quoted in
research-notes 2026-11-18 ("method M2") and in H-A5-06 to H-A5-08.

  python experiments/A5.17/m2_threshold_calibration.py
"""
import collections
import random
import statistics

from aegean.benchmark import lexicons as L, nulls
from aegean.benchmark.m2 import M2, M2Rules, SIGN_DOLGO


def main() -> None:
    vals = sorted(SIGN_DOLGO)
    rng = random.Random(99)
    strings = [tuple(rng.choice(vals) for _ in range(n)) for n in [2] * 300 + [3] * 400 + [4] * 200 + [5] * 100]
    lex = {k: L.REGISTRY[k]() for k in ("hebrew-strong-verbs-dolgo", "english-verbs-dolgo", "turkish-verbs-dolgo")}
    for th in (0.0, 0.25, 1 / 3):
        m = M2(M2Rules(max_distance=th))
        el = [g for g in strings if m.eligible(g)]
        row = []
        for k, lx in lex.items():
            real = sum(m.hits(el, m.prepare(lx))) / len(el)
            null = [sum(m.hits(el, m.prepare(nulls.stratified_matched_lexicon(lx, m, random.Random(i))))) / len(el)
                    for i in range(20)]
            row.append(f"{k.split('-')[0]} real {real:.3f} null {statistics.fmean(null):.3f}")
        by = collections.defaultdict(list)
        for g, h in zip(el, m.hits(el, m.prepare(lex["english-verbs-dolgo"]))):
            by[len(m.skeleton(g))].append(h)
        print(f"theta={th:.3f} eligible {len(el)} | " + " | ".join(row))
        print("   English by class count:", {k: round(statistics.fmean(v), 2) for k, v in sorted(by.items())})


if __name__ == "__main__":
    main()
