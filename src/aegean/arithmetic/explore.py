"""EXPLORATORY census of every KU-RO, KI-RO and PO-TO-KU-RO occurrence.

Not a pre-registered test (requested by Marius 2026-11-05 after H-A2-08). It
includes damaged rows and fraction-bearing rows, and evaluates fractions under
two published value sets. Nothing computed here can confirm a hypothesis on
corpus-v0.1; see research-notes 2026-11-05.
"""
from __future__ import annotations

import csv
from fractions import Fraction as F
from pathlib import Path

from aegean.arithmetic.census import tablet_of
from aegean.arithmetic.parse import MARKERS, parse_document

NEAR = {1, 10, 100, 1000}

# Corazza et al. 2021, Table 8 (verified from the PDF). H and A tentative in the paper.
CORAZZA = {"J": F(1, 2), "E": F(1, 4), "F": F(1, 8), "B": F(1, 5), "D": F(1, 6), "K": F(1, 10),
           "L2": F(1, 20), "L3": F(1, 30), "L4": F(1, 40), "L6": F(1, 60), "H": F(1, 16), "A": F(1, 24)}
# Schrijver 2014 as tabulated in Corazza et al. 2021, Table 3 (column read from the PDF text and
# cross-checked against Table 3's combination rows, e.g. J E B = 11/12, F K = 3/16). L-series marked "?" there.
SCHRIJVER = {"J": F(1, 2), "E": F(1, 4), "F": F(1, 8), "B": F(1, 6), "D": F(1, 5), "K": F(1, 16),
             "H": F(1, 3), "A": F(1, 12), "L2": F(1, 24), "L3": F(1, 36), "L4": F(1, 48), "L6": F(1, 64)}
VALUE_SETS = {"corazza2021": CORAZZA, "schrijver2014": SCHRIJVER}
LIGATURES = {"JE": ("J", "E"), "DD": ("D", "D")}


def value(integer, fractions, vs) -> F | None:
    """Exact value of a quantity, or None if a fraction sign has no value in this set."""
    total = F(integer or 0)
    for f in fractions:
        parts = LIGATURES.get(f, (f,))
        if any(p not in vs for p in parts):
            return None
        total += sum(vs[p] for p in parts)
    return total


def status(total: F | None, s: F | None, integer_only: bool) -> str:
    if total is None or s is None:
        return "unvalued"
    d = total - s
    if d == 0:
        return "exact"
    if integer_only and abs(d) in NEAR:
        return "near_miss_one_stroke"
    return "mismatch"


def _fmt(q):
    i, fr = q
    return " ".join(([str(i)] if i is not None else []) + fr) or "-"


def rows(docs, checks: dict) -> list[dict]:
    by_tablet = {}
    for d in docs:
        by_tablet.setdefault(tablet_of(d["id"]), []).append(d)
    out = []
    for d in docs:
        entries, _ = parse_document(d)
        mlines = sorted({i for i, ln in enumerate(d["lines"]) for t in ln
                         if t["type"] == "group" and tuple(t["signs"]) in MARKERS})
        for line in mlines:
            names = {MARKERS[tuple(t["signs"])] for t in d["lines"][line] if t["type"] == "group" and tuple(t["signs"]) in MARKERS}
            for marker in sorted(names):
                tot = next((e for e in entries if e.line == line and e.marker == marker), None)
                tq = (tot.quantity.integer, list(tot.quantity.fractions)) if tot else (None, [])
                prev = max([l for l in mlines if l < line], default=-1)
                if marker == "PO-TO-KU-RO":
                    sides = by_tablet[tablet_of(d["id"])]
                    allp = [e for sd in sides for e in parse_document(sd)[0]]
                    scopes = {"P1": [e for e in allp if e.marker == "KU-RO"], "P2": [e for e in allp if e.marker is None]}
                else:
                    scopes = {"S1": [e for e in entries if prev < e.line < line and e.marker is None],
                              "S2": [e for e in entries if e.marker is None]}
                chk = checks.get((d["id"], marker, line))
                for sc, ents in scopes.items():
                    eq = [(e.quantity.integer, list(e.quantity.fractions)) for e in ents]
                    integer_only = not tq[1] and not any(fr for _, fr in eq)
                    row = {
                        "doc": d["id"], "tablet": tablet_of(d["id"]), "site": d["site"], "marker": marker, "line": line,
                        "scope": sc, "total": _fmt(tq), "n_entries": len(ents),
                        "entries": "; ".join(_fmt(q) for q in eq), "integer_only": integer_only,
                        "gorila_checked": bool(chk),
                        "gorila_total_intact": chk["total_intact"] if chk else "",
                        "gorila_scope_intact": chk["scope_entries_intact"] if chk else "",
                        "gorila_entry_area_complete": chk["entry_area_complete"] if chk else "",
                        "parser_total_damaged": bool(tot and tot.quantity.damaged),
                        "parser_scope_damaged": sum(e.quantity.damaged for e in ents),
                    }
                    if chk:
                        clean = chk["total_intact"] == "yes" and (sc not in ("S1", "P1") or chk["scope_entries_intact"] == "yes") \
                            and (sc in ("S1", "P1") or (chk["scope_entries_intact"] == "yes" and not row["parser_scope_damaged"]))
                    else:
                        clean = not row["parser_total_damaged"] and not row["parser_scope_damaged"]
                    row["damage_class"] = ("clean" if clean else "damaged") + ("" if chk else " (parser only)")
                    for name, vs in VALUE_SETS.items():
                        if tot is None:
                            row[f"{name}_status"] = "no_total"
                            row[f"{name}_total"] = row[f"{name}_sum"] = row[f"{name}_diff"] = ""
                            continue
                        tv = value(*tq, vs)
                        sv = None if any(value(*q, vs) is None for q in eq) else sum((value(*q, vs) for q in eq), F(0))
                        row[f"{name}_total"] = "" if tv is None else str(tv)
                        row[f"{name}_sum"] = "" if sv is None else str(sv)
                        row[f"{name}_diff"] = "" if tv is None or sv is None else str(tv - sv)
                        row[f"{name}_status"] = status(tv, sv, integer_only) if ents else "empty_scope"
                    out.append(row)
    return out


def kiro_relations(docs, vs) -> list[dict]:
    """For each KI-RO with a quantity on a side that also has a KU-RO with a quantity,
    test three candidate relations (exploratory): a) KI-RO = sum of its S1 entries;
    b) KU-RO = all unmarked entries on the side - KI-RO; c) KU-RO = all unmarked entries + KI-RO."""
    out = []
    for d in docs:
        entries, _ = parse_document(d)
        ki = [e for e in entries if e.marker == "KI-RO"]
        ku = [e for e in entries if e.marker == "KU-RO"]
        if not ki or not ku:
            continue
        unmarked = [e for e in entries if e.marker is None]
        allsum = None if any(value(e.quantity.integer, e.quantity.fractions, vs) is None for e in unmarked) \
            else sum((value(e.quantity.integer, e.quantity.fractions, vs) for e in unmarked), F(0))
        mlines = sorted({e.line for e in entries if e.marker})
        for k in ki:
            kv = value(k.quantity.integer, k.quantity.fractions, vs)
            prev = max([l for l in mlines if l < k.line], default=-1)
            s1 = [e for e in entries if prev < e.line < k.line and e.marker is None]
            s1v = None if any(value(e.quantity.integer, e.quantity.fractions, vs) is None for e in s1) \
                else sum((value(e.quantity.integer, e.quantity.fractions, vs) for e in s1), F(0))
            for u in ku:
                uv = value(u.quantity.integer, u.quantity.fractions, vs)
                ok = lambda a, b: "" if a is None or b is None else ("exact" if a == b else "mismatch")
                out.append({
                    "doc": d["id"], "kiro_line": k.line, "kuro_line": u.line,
                    "kiro": str(kv) if kv is not None else "unvalued", "kuro": str(uv) if uv is not None else "unvalued",
                    "kiro_s1_sum": str(s1v) if s1v is not None else "unvalued",
                    "all_unmarked_sum": str(allsum) if allsum is not None else "unvalued",
                    "damaged": bool(k.quantity.damaged or u.quantity.damaged or any(e.quantity.damaged for e in unmarked)),
                    "a_kiro_eq_its_entries": ok(kv, s1v) if s1 else "empty",
                    "b_kuro_eq_all_minus_kiro": ok(uv, None if allsum is None or kv is None else allsum - kv),
                    "c_kuro_eq_all_plus_kiro": ok(uv, None if allsum is None or kv is None else allsum + kv),
                })
    return out


def write_csv(path: Path, rows_: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows_)
