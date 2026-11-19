"""Lexicon-side validation of the pseudo-lexicon nulls (no Linear A, no control): committed for H-A5-09.

For each of the six lexicons (M1's three, M2's three) and each null (stratified, pooled bigram, position-aware
bigram), 100 draws from random.Random(0) ... random.Random(99):
- overlap: share of the real lexicon's expanded forms that also occur in the pseudo-lexicon;
- position TV: total-variation distance between real and pseudo per-position letter frequencies, weighted by the
  number of letters at each (length, position);
- bigram TV: total-variation distance between real and pseudo adjacent-letter-pair frequencies.

  python experiments/A5.17/null_validation.py
Writes experiments/A5.17/results/null-validation.json (generated).
"""
import collections
import json
import random
import statistics
from pathlib import Path

from aegean.benchmark import lexicons as L, nulls
from aegean.benchmark.m1 import M1
from aegean.benchmark.m2 import M2

OUT = Path(__file__).resolve().parent / "results/null-validation.json"
NULLS = {"stratified": nulls.stratified_matched_lexicon, "bigram": nulls.bigram_matched_lexicon,
         "posbigram": nulls.positional_bigram_matched_lexicon}
DRAWS = 100


def position_tv(real, fake):
    def freq(forms):
        c = collections.Counter((len(f), i, ch) for f in forms for i, ch in enumerate(f))
        t = collections.Counter((len(f), i) for f in forms for i in range(len(f)))
        return c, t
    cr, tr = freq(real)
    cf, tf = freq(fake)
    total = sum(tr.values())
    out = 0.0
    for key, n in tr.items():
        letters = sorted({k[2] for k in list(cr) + list(cf) if k[:2] == key})  # sorted: summation order fixed
        d = 0.5 * sum(abs(cr[key + (c,)] / n - (cf[key + (c,)] / tf[key] if tf[key] else 0)) for c in letters)
        out += n / total * d
    return out


def bigram_tv(real, fake):
    def freq(forms):
        c = collections.Counter(a + b for f in forms for a, b in zip(f, f[1:]))
        n = sum(c.values())
        return {k: v / n for k, v in c.items()}
    p, q = freq(real), freq(fake)
    return 0.5 * sum(abs(p.get(k, 0) - q.get(k, 0)) for k in set(p) | set(q))


def main() -> None:
    result = {"draws": DRAWS, "seeds": "random.Random(i), i = 0 .. 99", "rows": []}
    for method, names in ((M1(), ("hebrew-strong-verbs", "english-verbs", "turkish-verbs")),
                          (M2(), ("hebrew-strong-verbs-dolgo", "english-verbs-dolgo", "turkish-verbs-dolgo"))):
        for name in names:
            real = L.REGISTRY[name]()
            prepared = method.prepare(real)
            for kind, draw in NULLS.items():
                rows = []
                for i in range(DRAWS):
                    fake = draw(real, method, random.Random(i))
                    rows.append((len(method.prepare(fake) & prepared) / len(prepared),
                                 position_tv(real.forms, fake.forms), bigram_tv(real.forms, fake.forms)))
                row = {"method": method.name, "lexicon": name, "null": kind,
                       "overlap": statistics.fmean(r[0] for r in rows),
                       "position_tv": statistics.fmean(r[1] for r in rows),
                       "bigram_tv": statistics.fmean(r[2] for r in rows)}
                result["rows"].append(row)
                print(f"{method.name} {name:27s} {kind:10s} overlap {row['overlap']:.3f}  position TV "
                      f"{row['position_tv']:.3f}  bigram TV {row['bigram_tv']:.3f}")
    OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
