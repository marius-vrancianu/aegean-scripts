"""H-A2-07: consistency of the written order of fraction signs.

Implements hypotheses/H-A2-07.md exactly. The primary statistic is value-free.
"""
from __future__ import annotations

import collections
import random
from fractions import Fraction

from aegean.arithmetic.parse import parse_document

SEED = 20261104
N_PERM = 10_000

# Corazza et al. 2021, Table 8 (verified from the PDF 2026-11-05). Used only in
# the secondary test; H and A are tentative in the paper.
CORAZZA_TABLE8 = {
    "J": Fraction(1, 2), "E": Fraction(1, 4), "F": Fraction(1, 8), "B": Fraction(1, 5),
    "D": Fraction(1, 6), "K": Fraction(1, 10), "L2": Fraction(1, 20), "L3": Fraction(1, 30),
    "L4": Fraction(1, 40), "L6": Fraction(1, 60), "H": Fraction(1, 16), "A": Fraction(1, 24),
}
# Table 9 values for the two ligature codepoints; exploratory only (not in the frozen secondary test).
CORAZZA_TABLE9_LIGATURES = {"JE": Fraction(3, 4), "DD": Fraction(1, 3)}


def fraction_lists(docs, undamaged_only: bool = False) -> list[list[str]]:
    out = []
    for d in docs:
        entries, _ = parse_document(d)
        for e in entries:
            q = e.quantity
            if len(q.fractions) >= 2 and not (undamaged_only and q.damaged):
                out.append(list(q.fractions))
    return out


def adjacent_pairs(lists):
    """(distinct ordered pairs, count of identical-sign pairs)."""
    pairs, same = [], 0
    for fl in lists:
        for a, b in zip(fl, fl[1:]):
            if a == b:
                same += 1
            else:
                pairs.append((a, b))
    return pairs, same


def consistency(pairs) -> tuple[float, dict]:
    """Statistic C and the per-unordered-pair counts. Ties contribute 0."""
    n = collections.Counter(pairs)
    keys = {tuple(sorted(p)) for p in n}
    consistent, table = 0, {}
    for x, y in sorted(keys):
        a, b = n[(x, y)], n[(y, x)]
        table[f"{x}|{y}"] = {f"{x}>{y}": a, f"{y}>{x}": b}
        if a != b:
            consistent += max(a, b)
    return (consistent / len(pairs) if pairs else float("nan")), table


def majority_cycles(pairs) -> list[list[str]]:
    """Directed graph of majority orders (ties dropped); return its cycles' strongly connected components."""
    n = collections.Counter(pairs)
    edges = collections.defaultdict(set)
    for (x, y), c in n.items():
        if c > n[(y, x)]:
            edges[x].add(y)
    nodes = {v for p in pairs for v in p}
    index, low, stack, on, sccs, counter = {}, {}, [], set(), [], [0]

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in edges[v]:
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                sccs.append(sorted(comp))

    for v in sorted(nodes):
        if v not in index:
            strong(v)
    return sccs


def permutation_null(lists, observed_c: float, n_perm: int = N_PERM, seed: int = SEED) -> tuple[float, list[float]]:
    rng = random.Random(seed)
    cs, ge = [], 0
    for _ in range(n_perm):
        shuffled = []
        for fl in lists:
            fl2 = fl[:]
            rng.shuffle(fl2)
            shuffled.append(fl2)
        c, _ = consistency(adjacent_pairs(shuffled)[0])
        cs.append(c)
        ge += c >= observed_c
    return ge / n_perm, cs


def descending_share(pairs, values: dict) -> tuple[int, int, int]:
    """(strictly descending, valued pairs, skipped pairs)."""
    desc = valued = skipped = 0
    for a, b in pairs:
        if a in values and b in values:
            valued += 1
            desc += values[a] > values[b]
        else:
            skipped += 1
    return desc, valued, skipped


def decide(n_pairs: int, c: float, acyclic: bool, p: float) -> str:
    if n_pairs < 15:
        return "inconclusive (insufficient data)"
    if c >= 0.90 and acyclic and p < 0.01:
        return "supported"
    if c < 0.75 or p >= 0.05:
        return "not supported"
    return "inconclusive"
