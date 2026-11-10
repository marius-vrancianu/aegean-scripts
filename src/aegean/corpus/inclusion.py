"""Inclusion rules for the canonical document list (A1.6).

The rules are documented, with their counts and the alternatives, in
docs/inclusion-rules.md. The defaults below were DECIDED by Marius on
2026-11-10 (R3/R4, R7, R9) or kept as proposed (R5, R6, R8, R10); every rule is a parameter, so a different choice is one argument,
not a code change, and the effect of each rule is reported.

Two separate outputs per document:
- `listed`: whether it is in the canonical list at all (only held-out documents
  and, optionally, unresolved IDs are left out);
- `analysis_default`: whether analyses use it unless they say otherwise
  (A3/A4 sequence analyses; A2 selects by its own scope rules).
"""
from __future__ import annotations

import collections
from dataclasses import asdict, dataclass

from aegean.corpus.concordance import DocCluster


@dataclass(frozen=True)
class Rules:
    # R3/R4: content tiers that enter analyses by default.
    analysis_tiers: tuple[str, ...] = ("T1",)
    # R5: registers (from the GORILA series) that enter analyses by default.
    analysis_registers: tuple[str, ...] = ("administrative", "non_administrative")
    # R6: documents found outside Crete.
    analysis_off_crete: bool = True
    # R7: documents attested in a single source.
    analysis_single_source: bool = True
    # R9: documents GORILA brackets as lost / known only from reports (<n>).
    analysis_lost: bool = False
    # R10: IDs that could not be resolved to one document.
    list_unresolved: bool = True
    analysis_unresolved: bool = False


def tier(c: DocCluster) -> str:
    """T1 text / T2 single sign / T3 no identified sign, judged per source and taking the best source.

    T1: >= 2 identified signs, or >= 1 sign and >= 1 numeral, in one source (sides summed).
    T2: exactly 1 identified sign and no numeral in the best source.
    T3: no identified sign in any source (traces, unidentified signs, or numerals alone).
    """
    per = collections.defaultdict(lambda: [0, 0])
    for r in c.records:
        per[r.source][0] += r.signs
        per[r.source][1] += r.numerals
    best = "T3"
    for signs, nums in per.values():
        if signs >= 2 or (signs >= 1 and nums >= 1):
            return "T1"
        if signs == 1:
            best = "T2"
    return best


@dataclass
class Decision:
    key: str
    tier: str
    listed: bool
    analysis_default: bool
    reasons: list[str]  # every rule that excluded the document from the analysis default


def decide(c: DocCluster, rules: Rules = Rules()) -> Decision:
    t = tier(c)
    unresolved = "id_unresolved" in c.flags
    reasons = []
    if t not in rules.analysis_tiers:
        reasons.append(f"R3/R4 tier {t}")
    if c.register not in rules.analysis_registers:
        reasons.append(f"R5 register {c.register}")
    if c.off_crete and not rules.analysis_off_crete:
        reasons.append("R6 off Crete")
    if len(c.sources) == 1 and not rules.analysis_single_source:
        reasons.append("R7 single source")
    if c.lost and not rules.analysis_lost:
        reasons.append("R9 lost (<n>)")
    if unresolved and not rules.analysis_unresolved:
        reasons.append("R10 unresolved ID")
    listed = rules.list_unresolved or not unresolved
    return Decision(c.key, t, listed, listed and not reasons, reasons)


def summarise(clusters: list[DocCluster], rules: Rules = Rules()) -> dict:
    ds = [decide(c, rules) for c in clusters]
    return {
        "rules": asdict(rules),
        "documents": len(clusters),
        "listed": sum(d.listed for d in ds),
        "analysis_default": sum(d.analysis_default for d in ds),
        "by_tier": dict(collections.Counter(d.tier for d in ds)),
        "excluded_by_reason": dict(collections.Counter(r for d in ds for r in d.reasons)),
    }
