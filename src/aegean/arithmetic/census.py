"""H-A2-08 — census of integer totals. Implements hypotheses/H-A2-08.md.

Uses the committed GORILA checks (experiments/A2/gorila-checks/) and refuses to
run on any occurrence without one. No fraction values are used anywhere.
"""
from __future__ import annotations

import csv
import itertools
import math
import random
import re
from dataclasses import dataclass, field
from pathlib import Path

from aegean.arithmetic.parse import MARKERS, parse_document

SEED = 20261105
N_PERM = 10_000
NEAR = {1, 10, 100, 1000}
EXACT_MAX_N = 8  # enumerate all n! reassignments up to this size (8! = 40,320)
SCOPES_KURO = ("S1", "S2")
SCOPES_POTO = ("P1", "P2")


def tablet_of(doc_id: str) -> str:
    """'HT122a' -> 'HT122'; IDs without a trailing side letter are their own tablet."""
    return re.sub(r"(?<=\d)[ab]$", "", doc_id)


def load_checks(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return {(r["doc"], r["marker"], int(r["marker_line"])): r for r in csv.DictReader(f)}


@dataclass
class Row:
    doc: str
    marker: str
    line: int
    scope: str
    total: int | None
    total_fractions: list[str]
    entries: list[tuple[int | None, list[str], bool]]  # (integer, fractions, damaged-by-parser)
    category: str = ""
    entry_sum: int | None = None
    difference: int | None = None
    notes: list[str] = field(default_factory=list)


def _occurrences(docs):
    """Yield (doc, entries, marker, line, total-entry-or-None)."""
    for d in docs:
        entries, _ = parse_document(d)
        for i, ln in enumerate(d["lines"]):
            for t in ln:
                if t["type"] != "group":
                    continue
                sig = tuple(t["signs"])
                name = {("AB081", "AB002"): "KU-RO", ("AB011", "AB005", "AB081", "AB002"): "PO-TO-KU-RO"}.get(sig)
                if name:
                    tot = next((e for e in entries if e.line == i and e.marker == name), None)
                    yield d, entries, name, i, tot


def build_rows(docs) -> list[Row]:
    by_tablet: dict[str, list] = {}
    for d in docs:
        by_tablet.setdefault(tablet_of(d["id"]), []).append(d)
    rows = []
    for d, entries, marker, line, tot in _occurrences(docs):
        total = tot.quantity.integer if tot else None
        tfr = list(tot.quantity.fractions) if tot else []
        # Any marker group (KU-RO, KI-RO, PO-TO-KU-RO) bounds S1, with or without a number.
        marker_lines = sorted({i for i, ln in enumerate(d["lines"]) for t in ln
                               if t["type"] == "group" and tuple(t["signs"]) in MARKERS})
        if marker == "KU-RO":
            prev = max([l for l in marker_lines if l < line], default=-1)
            s1 = [e for e in entries if prev < e.line < line and e.marker is None]
            s2 = [e for e in entries if e.marker is None]
            scopes = {"S1": s1, "S2": s2}
        else:
            sides = by_tablet[tablet_of(d["id"])]
            kuro, allent = [], []
            for sd in sides:
                es, _ = parse_document(sd)
                kuro += [e for e in es if e.marker == "KU-RO"]
                allent += [e for e in es if e.marker is None]
            scopes = {"P1": kuro, "P2": allent}
        for name, scope in scopes.items():
            rows.append(Row(d["id"], marker, line, name, total, tfr,
                            [(e.quantity.integer, list(e.quantity.fractions), e.quantity.damaged) for e in scope]))
    return rows


def categorize(row: Row, check: dict, s1_ids: set | None = None) -> Row:
    """Apply the H-A2-08 category table. `check` is the GORILA row for this occurrence."""
    if row.total is None and not row.total_fractions:
        row.category = "1 untestable: no total"
        return row
    if row.total_fractions or any(fr for _, fr, _ in row.entries):
        row.category = "2 needs values"
        return row
    damaged = check["total_intact"] != "yes"
    if row.scope in ("S1", "P1"):
        damaged = damaged or check["scope_entries_intact"] != "yes"
    else:
        # Alternative scopes: the GORILA scope judgement covers S1/P1 entries;
        # entries outside them fall back on the parser's damage flags.
        damaged = damaged or check["scope_entries_intact"] != "yes" or any(dmg for _, _, dmg in row.entries)
    if damaged:
        row.category = "3 untestable: damaged"
        return row
    if not row.entries:
        row.category = "4 untestable: scope empty"
        return row
    row.entry_sum = sum(i for i, _, _ in row.entries if i is not None)
    row.difference = row.total - row.entry_sum
    if row.difference == 0:
        row.category = "5 consistent"
    elif abs(row.difference) in NEAR:
        row.category = "6 near miss"
    elif row.difference > 0 and check["entry_area_complete"] in ("no", "unclear"):
        row.category = "7 missing entries"
    else:
        row.category = "8 inconsistent"
    return row


def permutation_test(pairs: list[tuple[int, int]], n_perm: int = N_PERM, seed: int = SEED) -> dict:
    """pairs = (entry_sum, total) for testable rows. Totals are reassigned at random."""
    sums = [s for s, _ in pairs]
    totals = [t for _, t in pairs]
    obs_c = sum(s == t for s, t in pairs)
    obs_n = sum(abs(t - s) in NEAR for s, t in pairs)
    rng = random.Random(seed)
    ge, cs, ns = 0, [], []
    for _ in range(n_perm):
        sh = totals[:]
        rng.shuffle(sh)
        c = sum(s == t for s, t in zip(sums, sh))
        cs.append(c)
        ns.append(sum(abs(t - s) in NEAR for s, t in zip(sums, sh)))
        ge += c >= obs_c
    out = {"n": len(pairs), "observed_consistent": obs_c, "observed_near_miss": obs_n,
           "null_mean_consistent": sum(cs) / n_perm, "null_mean_near_miss": sum(ns) / n_perm,
           "p_monte_carlo": ge / n_perm}
    if len(pairs) <= EXACT_MAX_N:
        # The registered p is "the share of reassignments with >= observed consistent rows".
        # For small n, compute that share exactly instead of estimating it (review of Finding 002, M1).
        hits = sum(sum(s == t for s, t in zip(sums, perm)) >= obs_c for perm in itertools.permutations(totals))
        out["p_exact"] = hits / math.factorial(len(pairs))
        out["min_attainable_p"] = min_attainable_p(sums, totals)
    out["p"] = out.get("p_exact", out["p_monte_carlo"])
    return out


def min_attainable_p(sums: list, totals: list) -> float:
    """Smallest p the test could give with these totals (all matchable totals matched)."""
    best = max(sum(s == t for s, t in zip(sums, perm)) for perm in itertools.permutations(totals))
    hits = sum(sum(s == t for s, t in zip(sums, perm)) >= best for perm in itertools.permutations(totals))
    return hits / math.factorial(len(sums))


def decide(test: dict) -> str:
    if test["n"] < 5:
        return "descriptive only (fewer than 5 testable)"
    if test["p"] < 0.01:
        return "supported"
    if test["p"] >= 0.05:
        return "not supported"
    return "inconclusive"
