"""Independent rerun (by the author session) of the robustness checks in
docs/reviews/finding-002-review.md. EXPLORATORY; no hypothesis is tested.

  python experiments/A2/exploratory/rerun_review_checks.py
"""
import collections
import csv
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from aegean.arithmetic import order  # noqa: E402
from aegean.arithmetic.parse import parse_document  # noqa: E402

SEED = 20261106
CENSUS = REPO / "experiments/A2/exploratory/census-all.csv"
CORPUS = REPO / "data/processed/corpus-v0.1/documents.jsonl"


def census_rows():
    return [r for r in csv.DictReader(CENSUS.open()) if r["marker"] == "KU-RO" and r["scope"] == "S1"
            and r["corazza2021_status"] in ("exact", "near_miss_one_stroke", "mismatch")]


def perm(rows, n_perm, strata=None, seed=SEED):
    sums = [F(r["corazza2021_sum"]) for r in rows]
    tots = [F(r["corazza2021_total"]) for r in rows]
    obs = sum(s == t for s, t in zip(sums, tots))
    groups = collections.defaultdict(list)
    for i, r in enumerate(rows):
        groups[strata(sums[i]) if strata else 0].append(i)
    rng, ge, total = random.Random(seed), 0, 0
    for _ in range(n_perm):
        sh = tots[:]
        for idx in groups.values():
            vals = [tots[i] for i in idx]
            rng.shuffle(vals)
            for i, v in zip(idx, vals):
                sh[i] = v
        c = sum(s == t for s, t in zip(sums, sh))
        total += c
        ge += c >= obs
    return {"n": len(rows), "observed_exact": obs, "null_mean_exact": round(total / n_perm, 3),
            "p": ge / n_perm, "n_perm": n_perm}


def magnitude(s):
    return 0 if s < 10 else 1 if s < 100 else 2


def main():
    out = {}
    rows = census_rows()
    out["census_unstratified"] = perm(rows, 20000)
    out["census_stratified_by_sum_magnitude"] = perm(rows, 20000, strata=magnitude)
    drop = {"HT117a", "HT88", "HT94b", "HT104", "HT85a"}  # rosters, HT 104 (source of J = 1/2), HT 85a (damaged total)
    kept = [r for r in rows if r["doc"] not in drop]
    out["census_without_rosters_HT104_HT85a"] = perm(kept, 20000) | {
        "exact_docs": sorted(r["doc"] for r in kept if r["corazza2021_status"] == "exact")}

    docs = [json.loads(l) for l in CORPUS.open(encoding="utf-8")]
    lists = order.fraction_lists(docs)
    # one count per ordered pair per document
    per_doc = []
    for d in docs:
        es, _ = parse_document(d)
        seen = set()
        for e in es:
            f = e.quantity.fractions
            for a, b in zip(f, f[1:]):
                if a != b:
                    seen.add((a, b))
        per_doc += sorted(seen)
    c, _ = order.consistency(per_doc)
    out["order_one_count_per_pair_per_doc"] = {"pairs": len(per_doc), "C": c}
    # ligatures split: JE -> J, E; DD -> D, D (quantities with >= 2 signs after splitting)
    split_lists = []
    for d in docs:
        for e in parse_document(d)[0]:
            f = [p for x in e.quantity.fractions for p in {"JE": ("J", "E"), "DD": ("D", "D")}.get(x, (x,))]
            if len(f) >= 2:
                split_lists.append(f)
    pairs, same = order.adjacent_pairs(split_lists)
    c2, _ = order.consistency(pairs)
    p2, null = order.permutation_null(split_lists, c2, n_perm=10000, seed=SEED)
    out["order_ligatures_split"] = {"pairs": len(pairs), "C": round(c2, 4), "acyclic": not order.majority_cycles(pairs),
                                    "p": p2, "null_mean_C": round(sum(null) / len(null), 3)}
    path = REPO / "experiments/A2/exploratory/review-checks-rerun.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
