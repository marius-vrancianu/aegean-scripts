"""Cross-source disagreement report (A1.9).

  python -m aegean.corpus.disagreements

Compares the three sources document by document, on the layered witnesses
(A1.8) grouped by the A1.6 concordance, and writes:
- data/processed/disagreements/summary.json (committed): every count in
  docs/reports/A1.9-source-disagreements.md, plus short examples (document
  IDs and sign IDs only);
- data/processed/disagreements/items.jsonl (gitignored): every itemised
  disagreement, which quotes source readings.

What is compared (each pair of sources, on documents both have):
1. signs: word signs aligned by base sign ID (difflib); agreements, substitutions,
   variant-only differences, signs present in one source only, unidentified-vs-identified;
2. word division: within identical sign runs, whether the word boundaries match;
3. numerals: the ordered list of numeral values per document;
4. fractions: letters after expanding ligatures; ligature encoding and order differences;
5. damage: for words with identical signs in both sources, whether each records a break
   at the left / right edge (only where both record breaks at all);
plus document-level: coverage, content tier (A1.6), site names, periods, IDs.

Independence: all three sources rest ultimately on GORILA, and lineara.xyz was
built from Younger's earlier HTML pages. Agreement is not evidence of a correct
reading; disagreement locates editorial and encoding differences.
"""
from __future__ import annotations

import collections
import difflib
import itertools
import json
from pathlib import Path

from aegean.corpus import build_layers, concordance, inclusion, schema
from aegean.corpus.schema import Witness

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "data/processed/disagreements"
GROUP_KINDS = ("word", "logogram", "transaction", "unknown", "mixed")
PAIRS = [("lineara.xyz", "sigla"), ("lineara.xyz", "younger"), ("sigla", "younger")]


# --- per-source views of one document -------------------------------------------------

def _side_order(w: Witness) -> tuple:
    return (w.source_id,)


def words(ws: list[Witness]) -> list[dict]:
    """Word items of a document in reading order: base IDs, full IDs, breaks, doubt."""
    out = []
    for w in sorted(ws, key=_side_order):
        for ln in w.lines:
            for it in ln.items:
                # Sign groups: words and standalone signs alike. lineara.xyz has no roles, so its
                # logograms are "words"; SigLA and Younger give them their own items.
                toks = [t for t in it.tokens if not (t.sign_id and _is_fraction(t.sign_id))]
                if it.kind not in GROUP_KINDS or not toks:
                    continue
                it = type(it)(**{**it.__dict__, "tokens": toks})
                out.append({
                    "base": tuple(schema.base_id(t.sign_id) if t.sign_id else "?" for t in it.tokens),
                    "ids": tuple(t.sign_id or "?" for t in it.tokens),
                    "left": it.left_break if it.left_break is not None else (it.tokens[0].break_before or None),
                    "right": it.right_break if it.right_break is not None else (it.tokens[-1].break_after or None),
                    "doubt": tuple(t.doubtful for t in it.tokens),
                })
    return out


def numerals(ws: list[Witness]) -> list[int]:
    return [it.numeral_value for w in sorted(ws, key=_side_order) for ln in w.lines for it in ln.items
            if it.kind in ("numeral",) and it.numeral_value is not None]


def fractions(ws: list[Witness]) -> tuple[list[str], int]:
    """(letters with ligatures expanded, number of ligature tokens)."""
    letters, lig = [], 0
    for w in sorted(ws, key=_side_order):
        for ln in w.lines:
            for it in ln.items:
                for t in it.tokens:
                    if not t.sign_id or not _is_fraction(t.sign_id):
                        continue
                    if t.components:
                        lig += 1
                        letters += [schema_letter(c) for c in t.components]
                    else:
                        letters.append(schema_letter(t.sign_id))
    return letters, lig


def _is_fraction(sid: str) -> bool:
    return sid[:2] == "A7" and len(sid) >= 4 and sid[1:4].isdigit()


def schema_letter(sid: str) -> str:
    from aegean.corpus.layers import l1_of
    return l1_of(sid) or sid


# --- pairwise comparisons ---------------------------------------------------------------

def compare_signs(wa: list[dict], wb: list[dict]) -> dict:
    a = [s for w in wa for s in w["base"]]
    b = [s for w in wb for s in w["base"]]
    ia = [s for w in wa for s in w["ids"]]
    ib = [s for w in wb for s in w["ids"]]
    c = collections.Counter()
    subs = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            c["agree"] += i2 - i1
            c["variant_only"] += sum(1 for i, j in zip(range(i1, i2), range(j1, j2)) if ia[i] != ib[j])
        elif op == "replace":
            n = min(i2 - i1, j2 - j1)
            for i, j in zip(range(i1, i1 + n), range(j1, j1 + n)):
                if "?" in (a[i], b[j]):
                    c["unidentified_in_one"] += 1
                else:
                    c["substitution"] += 1
                    subs.append((a[i], b[j]))
            c["only_a"] += (i2 - i1) - n
            c["only_b"] += (j2 - j1) - n
        elif op == "delete":
            c["only_a"] += i2 - i1
        elif op == "insert":
            c["only_b"] += j2 - j1
    return {"counts": c, "substitutions": subs}


def compare_division(wa: list[dict], wb: list[dict]) -> collections.Counter:
    """Within runs of identical signs, do the word boundaries fall in the same places?"""
    def bounds(ws):
        out, pos = set(), 0
        for w in ws:
            pos += len(w["base"])
            out.add(pos)
        return out, [s for w in ws for s in w["base"]]
    ba, sa = bounds(wa)
    bb, sb = bounds(wb)
    c = collections.Counter()
    for blk in difflib.SequenceMatcher(a=sa, b=sb, autojunk=False).get_matching_blocks():
        if blk.size < 2:
            continue
        inner_a = {p - blk.a for p in ba if blk.a < p < blk.a + blk.size}
        inner_b = {p - blk.b for p in bb if blk.b < p < blk.b + blk.size}
        c["runs"] += 1
        c["boundaries_both"] += len(inner_a & inner_b)
        c["boundary_only_a"] += len(inner_a - inner_b)
        c["boundary_only_b"] += len(inner_b - inner_a)
    return c


def compare_breaks(wa: list[dict], wb: list[dict]) -> collections.Counter:
    """For words with identical base signs, compare whether each edge is marked broken.
    Only edges where both sources record something (not None) are scored."""
    c = collections.Counter()
    ka = [w["base"] for w in wa]
    kb = [w["base"] for w in wb]
    for blk in difflib.SequenceMatcher(a=ka, b=kb, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            x, y = wa[blk.a + k], wb[blk.b + k]
            for edge in ("left", "right"):
                if x[edge] is None or y[edge] is None:
                    c[f"{edge}_not_comparable"] += 1
                    continue
                bx, by = bool(x[edge]), bool(y[edge])
                c[f"{edge}_{'agree' if bx == by else 'differ'}"] += 1
                if bx and not by:
                    c[f"{edge}_broken_only_a"] += 1
                if by and not bx:
                    c[f"{edge}_broken_only_b"] += 1
    return c


# --- the report -----------------------------------------------------------------------------

def run() -> tuple[dict, list[dict]]:
    ws, val = build_layers.all_witnesses()
    clusters, _ = concordance.build()
    by_rec = {}
    for c in clusters:
        for r in c.records:
            by_rec[(r.source, r.source_id)] = c.key
    by_doc = collections.defaultdict(lambda: collections.defaultdict(list))
    for w in ws:
        k = by_rec.get((w.source, w.source_id))
        if k:
            by_doc[k][w.source].append(w)
    cl = {c.key: c for c in clusters}
    items: list[dict] = []
    summary: dict = {"documents": len(clusters), "pairs": {}}

    # document-level: coverage and tiers
    summary["coverage"] = dict(collections.Counter("+".join(c.sources) for c in clusters))
    summary["coverage_by_support"] = {
        s: dict(collections.Counter("+".join(c.sources) for c in clusters if c.support == s))
        for s in sorted({c.support for c in clusters})}
    tier_dis = []
    for c in clusters:
        per = {}
        for src in c.sources:
            sub = concordance.DocCluster(c.key, [], c.site, c.series, c.support, c.register, c.off_crete,
                                         c.lost, [], [r for r in c.records if r.source == src])
            per[src] = inclusion.tier(sub)
        if len(set(per.values())) > 1:
            tier_dis.append({"doc": c.key, **per})
    summary["tier_disagreements"] = {"documents": len(tier_dis), "examples": tier_dis[:12],
                                     "patterns": dict(collections.Counter(
                                         " / ".join(f"{k}:{v}" for k, v in sorted(d.items()) if k != "doc")
                                         for d in tier_dis).most_common(10))}
    # metadata: site names and periods
    site_dis, period_dis = [], []
    for k, srcs in by_doc.items():
        names = {r.source: r.site_name for r in cl[k].records if r.site_name}
        if len({n.lower() for n in names.values()}) > 1:
            site_dis.append({"doc": k, **names})
        periods = {s: next((w.period for w in v if w.period), None) for s, v in srcs.items()}
        periods = {s: p for s, p in periods.items() if p}
        if len(periods) > 1 and len({p.replace(" ", "").upper() for p in periods.values()}) > 1:
            period_dis.append({"doc": k, **periods})
    summary["site_name_disagreements"] = {"documents": len(site_dis), "examples": site_dis[:15]}
    summary["period_disagreements"] = {
        "documents": len(period_dis), "examples": period_dis[:15],
        "patterns": dict(collections.Counter(
            f"{d.get('lineara.xyz')} | {d.get('sigla')}" for d in period_dis).most_common(15))}
    summary["id_differences"] = {
        "join_or_key_differs": [(c.key, c.aliases) for c in clusters if "join_or_key_differs" in c.flags],
        "lost_angle_bracket_disagreement": [c.key for c in clusters if c.lost and len(
            {"<" in r.source_id for r in c.records}) > 1],
        "sigla_metadata_id_mismatch": [f for w in ws if w.source == "sigla" for f in w.flags
                                       if f.startswith("metadata_id=")],
    }

    # pairwise content comparisons
    for sa, sb in PAIRS:
        tot = collections.Counter()
        div = collections.Counter()
        brk = collections.Counter()
        subs = collections.Counter()
        num = collections.Counter()
        frac = collections.Counter()
        docs_with_sign_diff = 0
        for k, srcs in sorted(by_doc.items()):
            if sa not in srcs or sb not in srcs:
                continue
            tot["documents"] += 1
            wa, wb = words(srcs[sa]), words(srcs[sb])
            r = compare_signs(wa, wb)
            tot.update(r["counts"])
            subs.update(r["substitutions"])
            if r["counts"]["substitution"] or r["counts"]["only_a"] or r["counts"]["only_b"]:
                docs_with_sign_diff += 1
                items.append({"type": "signs", "pair": f"{sa}|{sb}", "doc": k, **dict(r["counts"]),
                              "substitutions": r["substitutions"][:20]})
            div.update(compare_division(wa, wb))
            brk.update(compare_breaks(wa, wb))
            # numerals (SigLA has none)
            if "sigla" not in (sa, sb):
                na, nb = numerals(srcs[sa]), numerals(srcs[sb])
                if na or nb:
                    num["documents_with_numerals"] += 1
                    if na == nb:
                        num["identical_sequence"] += 1
                    elif sorted(na) == sorted(nb):
                        num["same_values_different_order"] += 1
                        items.append({"type": "numerals_order", "pair": f"{sa}|{sb}", "doc": k, "a": na, "b": nb})
                    elif sum(na) == sum(nb):
                        num["same_sum_different_split"] += 1
                        items.append({"type": "numerals_split", "pair": f"{sa}|{sb}", "doc": k, "a": na, "b": nb})
                    else:
                        num["different"] += 1
                        items.append({"type": "numerals", "pair": f"{sa}|{sb}", "doc": k, "a": na, "b": nb})
            fa, la = fractions(srcs[sa])
            fb, lb = fractions(srcs[sb])
            if fa or fb:
                frac["documents_with_fractions"] += 1
                if la or lb:
                    frac["documents_with_ligature_tokens"] += 1
                if not fa or not fb:
                    frac[f"fractions_only_in_{sa if fa else sb}"] += 1
                    items.append({"type": "fractions_absent", "pair": f"{sa}|{sb}", "doc": k, "a": fa, "b": fb})
                elif fa == fb:
                    frac["identical_letters"] += 1
                elif sorted(fa) == sorted(fb):
                    frac["same_letters_different_order"] += 1
                    items.append({"type": "fractions_order", "pair": f"{sa}|{sb}", "doc": k, "a": fa, "b": fb})
                else:
                    frac["different_letters"] += 1
                    items.append({"type": "fractions", "pair": f"{sa}|{sb}", "doc": k, "a": fa, "b": fb})
        aligned = tot["agree"] + tot["substitution"] + tot["unidentified_in_one"]
        summary["pairs"][f"{sa}|{sb}"] = {
            "documents": tot["documents"],
            "documents_with_sign_differences": docs_with_sign_diff,
            "signs": {k: tot[k] for k in ("agree", "variant_only", "substitution", "unidentified_in_one",
                                          "only_a", "only_b")},
            "sign_agreement_rate_aligned": round(tot["agree"] / aligned, 4) if aligned else None,
            "top_substitutions": [[a, b, n] for (a, b), n in subs.most_common(15)],
            "word_division": dict(div),
            "breaks": dict(brk),
            "numerals": dict(num) if "sigla" not in (sa, sb) else "n/a (SigLA records no numeral values)",
            "fractions": dict(frac),
        }

    # value level: Younger's printed value vs uniform L1
    vdiff = collections.Counter()
    for w in ws:
        if w.source != "younger":
            continue
        for t in w.tokens():
            if t.l1_value and t.l1 and t.l1_value != t.l1 and t.role != "logogram":
                vdiff[(t.l1_value, t.l1)] += 1
    summary["younger_value_vs_l1"] = [[a, b, n] for (a, b), n in vdiff.most_common(20)]
    summary["younger_vs_sigla_value_map_validation"] = {k: val[k] for k in ("documents_paired", "aligned", "agree", "disagree")}
    summary["sigla_internal"] = {"AB072_value": "SigLA gives ko; Unicode Linear B gives PE; SigLA also gives ko to AB070"}
    return summary, items


def write(out: Path = OUT) -> dict:
    summary, items = run()
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=list) + "\n",
                                      encoding="utf-8")
    (out / "items.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False, default=list) + "\n" for i in items),
                                     encoding="utf-8")
    return summary


if __name__ == "__main__":
    s = write()
    for p, v in s["pairs"].items():
        print(p, v["documents"], v["signs"], v["sign_agreement_rate_aligned"])
