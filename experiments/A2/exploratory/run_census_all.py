"""EXPLORATORY: census of all KU-RO / KI-RO / PO-TO-KU-RO occurrences on corpus-v0.1.

  python experiments/A2/exploratory/run_census_all.py
Writes census-all.csv, kiro-relations-<valueset>.csv and SUMMARY.md next to this file.
"""
import collections
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from aegean.arithmetic import explore  # noqa: E402
from aegean.arithmetic.census import load_checks  # noqa: E402

HERE = Path(__file__).resolve().parent
CORPUS = REPO / "data/processed/corpus-v0.1/documents.jsonl"
CHECKS = REPO / "experiments/A2/gorila-checks/checks-2026-11-05.csv"


def main():
    docs = [json.loads(l) for l in CORPUS.open(encoding="utf-8")]
    rows = explore.rows(docs, load_checks(CHECKS))
    explore.write_csv(HERE / "census-all.csv", rows)
    rel = {name: explore.kiro_relations(docs, vs) for name, vs in explore.VALUE_SETS.items()}
    for name, r in rel.items():
        if r:
            explore.write_csv(HERE / f"kiro-relations-{name}.csv", r)

    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    md = ["# EXPLORATORY census of all accounting markers (generated)", "",
          f"corpus-v0.1, code {commit[:7]}. **Not a pre-registered test.** See research-notes 2026-11-05.", ""]
    for marker in ("KU-RO", "KI-RO", "PO-TO-KU-RO"):
        for vsn in explore.VALUE_SETS:
            md += [f"## {marker} — value set `{vsn}`", "",
                   "| Scope | Damage class | " + " | ".join(["exact", "near_miss_one_stroke", "mismatch", "unvalued", "empty_scope", "no_total"]) + " |",
                   "|---|---|" + "---|" * 6]
            c = collections.Counter((r["scope"], r["damage_class"], r[f"{vsn}_status"]) for r in rows if r["marker"] == marker)
            for sc, dc in sorted({(s, d) for s, d, _ in c}):
                md.append(f"| {sc} | {dc} | " + " | ".join(str(c[(sc, dc, st)]) for st in
                          ["exact", "near_miss_one_stroke", "mismatch", "unvalued", "empty_scope", "no_total"]) + " |")
            md.append("")
    md += ["## Exact matches and one-stroke near misses (primary scopes S1/P1)", "",
           "| Doc | Marker | Total | Entries | Damage | Corazza | Schrijver |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["scope"] in ("S1", "P1") and ({r["corazza2021_status"], r["schrijver2014_status"]} & {"exact", "near_miss_one_stroke"}):
            md.append(f"| {r['doc']} | {r['marker']} | {r['total']} | {r['n_entries']} | {r['damage_class']} | "
                      f"{r['corazza2021_status']} ({r['corazza2021_diff']}) | {r['schrijver2014_status']} ({r['schrijver2014_diff']}) |")
    md += ["", "## KI-RO relations (exploratory; 3 relations per KI-RO/KU-RO pair)", ""]
    for name, r in rel.items():
        cnt = collections.Counter()
        for x in r:
            for k in ("a_kiro_eq_its_entries", "b_kuro_eq_all_minus_kiro", "c_kuro_eq_all_plus_kiro"):
                cnt[(k, x[k] or "unvalued")] += 1
        md.append(f"- `{name}`: {len(r)} KI-RO/KU-RO pairs; " + "; ".join(f"{k}: {dict((v, cnt[(k, v)]) for v in ('exact', 'mismatch', 'unvalued', 'empty') if cnt[(k, v)])}"
                            for k in ("a_kiro_eq_its_entries", "b_kuro_eq_all_minus_kiro", "c_kuro_eq_all_plus_kiro")))
        for x in r:
            if "exact" in (x["a_kiro_eq_its_entries"], x["b_kuro_eq_all_minus_kiro"], x["c_kuro_eq_all_plus_kiro"]):
                md.append(f"  - {x['doc']} (KI-RO line {x['kiro_line']}, KU-RO line {x['kuro_line']}, damaged={x['damaged']}): "
                          f"a={x['a_kiro_eq_its_entries']}, b={x['b_kuro_eq_all_minus_kiro']}, c={x['c_kuro_eq_all_plus_kiro']}")
    (HERE / "SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
