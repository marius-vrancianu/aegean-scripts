"""A2.2 — inventory of documents with KU-RO / KI-RO / PO-TO-KU-RO.

  python -m aegean.arithmetic.inventory  > experiments/A2/inventory-corpus-v0.1.csv

Deliberately computes NO sums and uses NO fraction values. It records, for
each marker occurrence, its quantity (symbolic), the entries that could fall
in its scope, and damage, and assigns a provisional class by the rules in
experiments/A2/inventory-rules.md. Whether totals add up is decided later
(A2.6) under scope and tolerance rules frozen in the hypothesis files.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from aegean.arithmetic.parse import MARKERS, parse_document

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "data/processed/corpus-v0.1/documents.jsonl"

FIELDS = [
    "doc", "site", "support", "scribe", "period", "marker", "marker_line", "n_markers_in_doc",
    "total_integer", "total_fractions", "total_damaged",
    "scope_entries", "scope_damaged", "scope_unlabelled", "scope_fraction_signs",
    "doc_lacunae", "doc_warnings", "class", "reason",
]


def marker_lines(doc) -> list[tuple[int, str]]:
    out = []
    for i, ln in enumerate(doc["lines"]):
        for t in ln:
            if t["type"] == "group" and tuple(t["signs"]) in MARKERS:
                out.append((i, MARKERS[tuple(t["signs"])]))
    return out


def classify(row: dict) -> tuple[str, str]:
    """Provisional class. Rules: experiments/A2/inventory-rules.md (R1-R5)."""
    if row["total_integer"] == "" and row["total_fractions"] == "":
        return "indeterminate", "R1: marker has no quantity on its line"
    if row["scope_entries"] == 0:
        return "indeterminate", "R2: no entries before the marker"
    if row["total_damaged"]:
        return "damaged", "R3: the total itself is damaged"
    if row["scope_damaged"] or row["doc_warnings"]:
        return "damaged", "R4: damaged entry or unparsed token in scope"
    if row["n_markers_in_doc"] > 1 or row["scope_unlabelled"]:
        return "complete-scope-unclear", "R5: several markers or unlabelled quantities; scope rule needed"
    return "complete", "R6: total and every entry in scope intact"


def inventory(docs) -> list[dict]:
    rows = []
    for d in docs:
        mlines = marker_lines(d)
        if not mlines:
            continue
        entries, warnings = parse_document(d)
        lacunae = sum(1 for ln in d["lines"] for t in ln if t["type"] == "lacuna" or t["damaged_left"] or t["damaged_right"])
        prev = -1
        for line_no, marker in mlines:
            tot = next((e for e in entries if e.line == line_no and e.marker == marker), None)
            scope = [e for e in entries if prev < e.line < line_no and e.marker is None]
            row = {
                "doc": d["id"], "site": d["site"], "support": d["support"], "scribe": d["scribe"],
                "period": d["period"], "marker": marker, "marker_line": line_no, "n_markers_in_doc": len(mlines),
                "total_integer": "" if tot is None or tot.quantity.integer is None else tot.quantity.integer,
                "total_fractions": "" if tot is None else " ".join(tot.quantity.fractions),
                "total_damaged": bool(tot and tot.quantity.damaged),
                "scope_entries": len(scope),
                "scope_damaged": sum(e.quantity.damaged for e in scope),
                "scope_unlabelled": sum(not e.label_on_line for e in scope),
                "scope_fraction_signs": " ".join(sorted({f for e in scope for f in e.quantity.fractions})),
                "doc_lacunae": lacunae,
                "doc_warnings": len(warnings),
            }
            row["class"], row["reason"] = classify(row)
            rows.append(row)
            prev = line_no
    return rows


def main() -> None:
    docs = [json.loads(l) for l in CORPUS.open(encoding="utf-8")]
    rows = inventory(docs)
    w = csv.DictWriter(sys.stdout, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)


if __name__ == "__main__":
    main()
