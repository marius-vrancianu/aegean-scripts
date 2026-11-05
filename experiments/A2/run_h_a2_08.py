"""Run H-A2-08 on corpus-v0.1; write experiments/A2/results/H-A2-08.{json,md}."""
import collections
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from aegean.arithmetic import census  # noqa: E402

CORPUS = REPO / "data/processed/corpus-v0.1/documents.jsonl"
CHECKS = REPO / "experiments/A2/gorila-checks/checks-2026-11-05.csv"
MANIFEST = json.loads((REPO / "data/processed/corpus-v0.1/MANIFEST.json").read_text())


def main() -> None:
    docs = [json.loads(l) for l in CORPUS.open(encoding="utf-8")]
    checks = census.load_checks(CHECKS)
    rows = census.build_rows(docs)
    missing = {(r.doc, r.marker, r.line) for r in rows} - set(checks)
    if missing:
        raise SystemExit(f"no committed GORILA check for {sorted(missing)}; refusing to run (H-A2-08 step 1)")
    rows = [census.categorize(r, checks[(r.doc, r.marker, r.line)]) for r in rows]

    table = collections.defaultdict(collections.Counter)
    for r in rows:
        table[r.scope][r.category] += 1
    testable = [(r.entry_sum, r.total) for r in rows if r.scope == "S1" and r.category[0] in "5678"]
    test = census.permutation_test(testable)
    test["decision"] = census.decide(test)

    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {
        "hypothesis": "H-A2-08",
        "corpus": f"{MANIFEST['version']} (sha256 {MANIFEST['documents_jsonl_sha256']})",
        "gorila_checks": CHECKS.name,
        "code_commit": commit,
        "seed": census.SEED, "n_permutations": census.N_PERM,
        "category_table": {k: dict(sorted(v.items())) for k, v in sorted(table.items())},
        "primary_test_S1": test,
        "rows": [{k: v for k, v in asdict(r).items() if k != "entries"} | {"n_entries": len(r.entries)} for r in rows],
    }
    res = REPO / "experiments/A2/results"
    res.mkdir(parents=True, exist_ok=True)
    (res / "H-A2-08.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    cats = sorted({r.category for r in rows})
    md = ["# H-A2-08 results (generated)", "", "| Category | " + " | ".join(sorted(table)) + " |",
          "|---|" + "---|" * len(table)]
    for c in cats:
        md.append(f"| {c} | " + " | ".join(str(table[s].get(c, 0)) for s in sorted(table)) + " |")
    md += ["", "## Testable rows (categories 5–8), all scopes", "",
           "| Doc | Marker | Scope | Entries | Sum | Total | Difference | Category |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.category[0] in "5678":
            md.append(f"| {r.doc} | {r.marker} | {r.scope} | {len(r.entries)} | {r.entry_sum} | {r.total} | {r.difference} | {r.category} |")
    md += ["", "## Primary test (S1)", "", "```", json.dumps(test, indent=2), "```"]
    (res / "H-A2-08.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
