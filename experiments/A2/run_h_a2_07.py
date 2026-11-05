"""Run H-A2-07 on corpus-v0.1 and write experiments/A2/results/H-A2-07.json."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from aegean.arithmetic import order  # noqa: E402

CORPUS = REPO / "data/processed/corpus-v0.1/documents.jsonl"
MANIFEST = json.loads((REPO / "data/processed/corpus-v0.1/MANIFEST.json").read_text())


def run(undamaged_only: bool) -> dict:
    docs = [json.loads(l) for l in CORPUS.open(encoding="utf-8")]
    lists = order.fraction_lists(docs, undamaged_only)
    pairs, same = order.adjacent_pairs(lists)
    c, table = order.consistency(pairs)
    cycles = order.majority_cycles(pairs)
    p, null = order.permutation_null(lists, c)
    null_sorted = sorted(null)
    res = {
        "quantities_with_2plus_fraction_signs": len(lists),
        "adjacent_distinct_pairs": len(pairs),
        "identical_sign_pairs_excluded": same,
        "C": c,
        "pair_table": table,
        "majority_cycles": cycles,
        "acyclic": not cycles,
        "p_permutation": p,
        "null_C_mean": sum(null) / len(null),
        "null_C_95th_percentile": null_sorted[int(0.95 * len(null)) - 1],
        "decision": order.decide(len(pairs), c, not cycles, p),
    }
    d, v, s = order.descending_share(pairs, order.CORAZZA_TABLE8)
    res["secondary_table8"] = {"descending": d, "valued_pairs": v, "skipped_pairs": s,
                               "label": "consistency check, not independent evidence (descending order is Corazza premise 5)"}
    d2, v2, s2 = order.descending_share(pairs, {**order.CORAZZA_TABLE8, **order.CORAZZA_TABLE9_LIGATURES})
    res["exploratory_table8_plus_ligatures"] = {"descending": d2, "valued_pairs": v2, "skipped_pairs": s2}
    return res


def main() -> None:
    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {
        "hypothesis": "H-A2-07",
        "corpus": f"{MANIFEST['version']} (documents.jsonl sha256 {MANIFEST['documents_jsonl_sha256']})",
        "code_commit": commit,
        "seed": order.SEED,
        "n_permutations": order.N_PERM,
        "primary_all_quantities": run(False),
        "secondary_undamaged_only": run(True),
    }
    path = REPO / "experiments/A2/results/H-A2-07.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
