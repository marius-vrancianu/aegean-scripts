"""Baseline statistics on the training split (A1.11; plan §0.7). Layer: L0.

  python -m aegean.corpus.baseline
  python -m aegean.corpus.baseline --witnesses PATH --allow-partial   # a build without all sources

Writes data/processed/baseline/baseline.json and
docs/reports/A1.11-baseline-statistics.md (both generated; do not edit).

Everything is computed on the training split of the default analysis set
(aegean.corpus.load), **per source**: the sources are never merged, so a
figure is reported once for each of lineara.xyz, SigLA and Younger.

Definitions (the same for every source)
- **Sign-group**: an item of kind word, logogram, transaction, unknown or
  mixed, without its fraction signs. lineara.xyz records no sign roles, so
  its single logograms are one-sign groups; SigLA and Younger mark them.
- **Sign**: a token with an L0 sign ID, counted by base ID (AB131a and AB131b
  are AB131). Tokens without an ID are counted as unidentified.
- **Multi-sign group**: a sign-group of two or more tokens. Lengths and
  positions are reported for these, because a one-sign group has no
  position and is usually a logogram.
- **Position**: in a multi-sign group, the first token is initial if the
  group's left edge is not marked broken; the last is final if the right
  edge is not marked broken; all tokens in between are medial. A token at a
  broken edge has no position and is counted under `edge_broken`.
- **Complete group**: both edges unbroken and every token identified.

Damage marking differs by source (docs/schema.md): lineara.xyz marks breaks
incompletely and never marks doubt, so its "complete" counts are upper
bounds.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

from aegean.corpus import load, resample
from aegean.corpus.layers import l1_of
from aegean.corpus.schema import base_id

REPO = Path(__file__).resolve().parents[3]
OUT_JSON = REPO / "data/processed/baseline/baseline.json"
OUT_MD = REPO / "docs/reports/A1.11-baseline-statistics.md"
SOURCES = ("lineara.xyz", "sigla", "younger")
SOURCE_ORDER = ("sigla", "lineara.xyz", "younger")  # primary reading for the intervals; see the report
GROUP_KINDS = ("word", "logogram", "transaction", "unknown", "mixed")
SEED = 11112026
N_RESAMPLES = 1000
TOP = 25


def _is_fraction(sign_id: str | None) -> bool:
    return bool(sign_id) and sign_id[:2] == "A7" and sign_id[1:4].isdigit()


def groups(ws: list[dict]):
    """Yield (witness, item, tokens) for every sign-group, fraction signs removed."""
    for w in ws:
        for ln in w["lines"]:
            for it in ln["items"]:
                if it["kind"] not in GROUP_KINDS:
                    continue
                toks = [t for t in it["tokens"] if not _is_fraction(t.get("sign_id"))]
                if toks:
                    yield w, it, toks


def _edge_intact(item: dict, tok: dict, side: str) -> bool:
    return not (item.get(f"{side}_break") or tok.get("break_before" if side == "left" else "break_after"))


def counts(ws: list[dict]) -> dict:
    """Every count for one list of witnesses (one source, or one resampling draw)."""
    c = collections.Counter()
    freq, pos = collections.Counter(), collections.defaultdict(collections.Counter)
    by_role = collections.defaultdict(collections.Counter)
    lengths, lengths_complete = collections.Counter(), collections.Counter()
    for w, it, toks in groups(ws):
        ids = [base_id(t["sign_id"]) if t.get("sign_id") else None for t in toks]
        c["sign_groups"] += 1
        c["tokens"] += len(toks)
        c["unidentified_tokens"] += ids.count(None)
        c["doubtful_tokens"] += sum(bool(t.get("doubtful")) for t in toks)
        for t, i in zip(toks, ids):
            if i:
                freq[i] += 1
                by_role[t.get("role") or "not_recorded"][i] += 1
        if len(toks) < 2:
            c["one_sign_groups"] += 1
            continue
        left, right = _edge_intact(it, toks[0], "left"), _edge_intact(it, toks[-1], "right")
        complete = left and right and None not in ids
        c["multi_sign_groups"] += 1
        c["multi_sign_groups_complete"] += complete
        c["multi_sign_tokens"] += len(toks)
        lengths[len(toks)] += 1
        if complete:
            lengths_complete[len(toks)] += 1
        for n, i in enumerate(ids):
            if i is None:
                continue
            if n == 0:
                pos[i]["initial" if left else "edge_broken"] += 1
            elif n == len(ids) - 1:
                pos[i]["final" if right else "edge_broken"] += 1
            else:
                pos[i]["medial"] += 1
    for w in ws:
        for ln in w["lines"]:
            for it in ln["items"]:
                c[f"items_{it['kind']}"] += 1
    return {"totals": dict(sorted(c.items())), "sign_frequency": dict(freq.most_common()),
            "position": {s: dict(p) for s, p in sorted(pos.items())},
            "sign_frequency_by_role": {r: dict(f.most_common()) for r, f in sorted(by_role.items())},
            "group_length": {str(k): v for k, v in sorted(lengths.items())},
            "group_length_complete": {str(k): v for k, v in sorted(lengths_complete.items())}}


def headline(ws: list[dict]) -> dict[str, float]:
    """A few scalar figures for the resampling intervals."""
    k = counts(ws)
    t, freq = k["totals"], k["sign_frequency"]
    identified = sum(freq.values())
    n_multi = t.get("multi_sign_groups", 0)
    top10 = sum(list(freq.values())[:10])
    hapax = sum(v == 1 for v in freq.values())
    return {
        "identified_sign_tokens": identified,
        "distinct_signs": len(freq),
        "signs_occurring_once": hapax,
        "top10_share": top10 / identified if identified else float("nan"),
        "multi_sign_groups": n_multi,
        "mean_multi_sign_group_length": t.get("multi_sign_tokens", 0) / n_multi if n_multi else float("nan"),
    }


def breakdown(ws: list[dict], docs: dict[str, dict], field: str) -> dict:
    """Documents, sign-groups and identified sign tokens by a document-list field (site, support, register)."""
    out = collections.defaultdict(lambda: {"documents": set(), "sign_groups": 0, "identified_tokens": 0})
    for w, it, toks in groups(ws):
        b = out[docs[w["doc_key"]][field]]
        b["documents"].add(w["doc_key"])
        b["sign_groups"] += 1
        b["identified_tokens"] += sum(bool(t.get("sign_id")) for t in toks)
    for w in ws:  # documents whose witnesses hold no sign-group still count as documents
        out[docs[w["doc_key"]][field]]["documents"].add(w["doc_key"])
    return {k: {**v, "documents": len(v["documents"])} for k, v in sorted(out.items())}


def by_period(ws: list[dict]) -> dict:
    """Documents by the period string exactly as each source gives it (not normalised)."""
    seen = collections.defaultdict(set)
    for w in ws:
        seen[w.get("period") or "(none given)"].add(w["doc_key"])
    return {k: len(v) for k, v in sorted(seen.items())}


def build(witnesses_path: Path = load.WITNESSES, allow_partial: bool = False, n: int = N_RESAMPLES) -> dict:
    docs = {r["key"]: r for r in load.documents()}
    ws = load.witnesses(path=witnesses_path, verify_hash=not allow_partial)
    by_source = collections.defaultdict(list)
    for w in ws:
        by_source[w["source"]].append(w)
    missing = [s for s in SOURCES if s not in by_source]
    if missing and not allow_partial:
        raise SystemExit(f"sources missing from {witnesses_path}: {missing}")
    corpus = resample.group(ws)
    site = lambda key: docs[key]["site"]  # noqa: E731
    site.__name__ = "site (document list)"
    out = {
        "task": "A1.11",
        "layer": "L0",
        "split": "train",
        "partial_build": bool(missing) or not _matches_release(witnesses_path),
        "sources_present": [s for s in SOURCES if s in by_source],
        "sources_missing": missing,
        "witnesses_sha256": hashlib.sha256(witnesses_path.read_bytes()).hexdigest(),
        "training_documents": len(docs),
        "training_documents_with_a_witness": len(corpus),
        "per_source": {},
        "resampling": resample.run(headline, corpus, source_order=SOURCE_ORDER, seed=SEED, n=n, stratum=site),
    }
    for s in out["sources_present"]:
        sw = by_source[s]
        out["per_source"][s] = {
            "documents": len({w["doc_key"] for w in sw}), "witnesses": len(sw),
            **counts(sw), "headline": headline(sw),
            "by_site": breakdown(sw, docs, "site"), "by_support": breakdown(sw, docs, "support"),
            "by_register": breakdown(sw, docs, "register"), "by_period_as_given": by_period(sw),
        }
    return out


def _matches_release(path: Path) -> bool:
    want = json.loads(load.RELEASE_MANIFEST.read_text(encoding="utf-8"))["components"]["witnesses"]["sha256"]
    return hashlib.sha256(path.read_bytes()).hexdigest() == want


# --- report ---------------------------------------------------------------------------------

def _name(sign: str) -> str:
    v = l1_of(sign)
    return f"{sign} ({v})" if v else sign


def _f(x, d=2) -> str:
    return f"{x:,.{d}f}" if isinstance(x, float) else f"{x:,}"


def render(b: dict) -> str:
    src = b["sources_present"]
    L = ["# A1.11 — Baseline statistics, training split", "",
         "Generated by `python -m aegean.corpus.baseline` from `data/processed/baseline/baseline.json`. Do not edit.", ""]
    if b["partial_build"]:
        L += [f"> **PARTIAL BUILD.** Source(s) missing: {', '.join(b['sources_missing']) or 'none'}. This run used a witnesses "
              "file that is not the release file (the Younger PDFs cannot be fetched by script). Rerun on the full "
              "`witnesses.jsonl` to complete the report; the figures for the sources present do not change.", ""]
    L += ["**Scope.** Layer L0. Training split of the default analysis set only "
          f"({b['training_documents']} documents; the 90 held-out documents are not read). "
          "Figures are per source, never for a merged text. Sign names in brackets are conventional Linear B values "
          "(L1), given only as labels.", "",
          "**Status.** Descriptive counts, not a finding. No hypothesis is tested here. Definitions are in the "
          "module docstring of `aegean.corpus.baseline`; the main ones:",
          "- a *sign-group* is a word or a standalone sign (lineara.xyz does not separate logograms from words);",
          "- a *multi-sign group* has two or more signs; lengths and positions are counted on these;",
          "- *initial* and *final* are counted only where that edge of the group is not marked broken;",
          "- a *complete* group has both edges unbroken and every sign identified.", "",
          "## Coverage", "", "| | " + " | ".join(src) + " |", "|---|" + "---|" * len(src)]
    P = b["per_source"]
    rows = [("Documents with a witness", lambda p: p["documents"]),
            ("Witnesses (document sides)", lambda p: p["witnesses"]),
            ("Sign-groups", lambda p: p["totals"].get("sign_groups", 0)),
            ("— one-sign groups", lambda p: p["totals"].get("one_sign_groups", 0)),
            ("— multi-sign groups", lambda p: p["totals"].get("multi_sign_groups", 0)),
            ("— multi-sign groups, complete", lambda p: p["totals"].get("multi_sign_groups_complete", 0)),
            ("Sign tokens in sign-groups", lambda p: p["totals"].get("tokens", 0)),
            ("— identified", lambda p: p["headline"]["identified_sign_tokens"]),
            ("— unidentified", lambda p: p["totals"].get("unidentified_tokens", 0)),
            ("— marked doubtful", lambda p: p["totals"].get("doubtful_tokens", 0)),
            ("Distinct signs (base IDs)", lambda p: p["headline"]["distinct_signs"]),
            ("Signs occurring once", lambda p: p["headline"]["signs_occurring_once"]),
            ("Share of the ten most frequent signs", lambda p: f"{p['headline']['top10_share']:.1%}"),
            ("Mean length of multi-sign groups", lambda p: _f(p["headline"]["mean_multi_sign_group_length"])),
            ("Numeral items", lambda p: p["totals"].get("items_numeral", 0)),
            ("Fraction items", lambda p: p["totals"].get("items_fraction", 0))]
    for label, fn in rows:
        L.append(f"| {label} | " + " | ".join(_f(v) if not isinstance(v := fn(P[s]), str) else v for s in src) + " |")
    L += ["", "Reading the table: lineara.xyz marks no sign as doubtful or unidentified (damage is recorded as "
          "lacuna items), SigLA records no numerals, and Younger has no Haghia Triada. Differences between columns "
          "are mostly differences in coverage and encoding, not in readings (A1.9).", "",
          "## Intervals for the headline figures (A1.14 harness)", "",
          f"Seed {b['resampling']['params']['seed']}, {b['resampling']['params']['n']} resamples, "
          f"{int(b['resampling']['params']['level'] * 100)}% percentile intervals, "
          f"p_doubt {b['resampling']['params']['p_doubt']}. "
          f"Point estimate: one source per document, the first available of "
          f"{' > '.join(b['resampling']['params']['source_order'])} (SigLA first because it marks doubt and sign "
          "roles; this order is a convention). *Reading*: one source per document chosen at random, doubtful signs "
          "blanked half the time. *Bootstrap*: documents resampled within sites. *Both*: the two together.", "",
          "| Figure | Estimate | Reading | Bootstrap | Both |", "|---|---|---|---|---|"]
    R = b["resampling"]
    for name, est in R["estimate"].items():
        d = 3 if "share" in name else 2 if "mean" in name else 0
        cell = lambda k: f"{_f(float(R[k][name]['low']), d)} – {_f(float(R[k][name]['high']), d)}"  # noqa: E731
        L.append(f"| {name.replace('_', ' ')} | {_f(est, d) if isinstance(est, float) else _f(est)} | "
                 f"{cell('reading')} | {cell('bootstrap')} | {cell('both')} |")
    L += ["", "How to read this:",
          "- The intervals show how much a figure moves with the choice of source and with the sample of documents. "
          "They are not confidence intervals for a property of the language: the surviving documents are not a "
          "random sample of what was written.",
          "- The *reading* interval reflects two things: encoding differences between sources (A1.9), and the "
          "blanking of signs a source marks as doubtful (" +
          ", ".join(f"{x}: {P[x]['totals'].get('doubtful_tokens', 0)}" for x in src) +
          "). A source that marks no doubt contributes no such variation, which is a property of the source, "
          "not of the tablets.",
          "- **Counts of distinct signs and of signs occurring once fall outside their bootstrap intervals.** That is "
          "expected, not an error: a sample drawn with replacement always contains fewer distinct types than the "
          "original, so the bootstrap is biased downwards for any count of types. Use it for shares and means, "
          "not for inventory sizes.", ""]
    L += ["## Most frequent signs", "",
          f"The {TOP} most frequent signs per source, all sign-groups, with the share of that source's identified tokens.", "",
          "| Rank | " + " | ".join(src) + " |", "|---|" + "---|" * len(src)]
    tops = {s: list(P[s]["sign_frequency"].items())[:TOP] for s in src}
    for i in range(TOP):
        cells = []
        for s in src:
            if i < len(tops[s]):
                sign, n = tops[s][i]
                cells.append(f"{_name(sign)} {n} ({n / P[s]['headline']['identified_sign_tokens']:.1%})")
            else:
                cells.append("")
        L.append(f"| {i + 1} | " + " | ".join(cells) + " |")
    L += ["", "## Position in multi-sign groups (Packard-style table)", "",
          "Counts of each sign as initial / medial / final, for the 20 signs most frequent in multi-sign groups. "
          "\"Broken\" = the sign stands at an edge marked as broken, so its position is unknown.", ""]
    for s in src:
        pos = P[s]["position"]
        ranked = sorted(pos, key=lambda k: (-sum(pos[k].values()), k))[:20]
        L += [f"**{s}**", "", "| Sign | Initial | Medial | Final | Broken | Total |", "|---|---|---|---|---|---|"]
        for sign in ranked:
            p = pos[sign]
            L.append(f"| {_name(sign)} | {p.get('initial', 0)} | {p.get('medial', 0)} | {p.get('final', 0)} | "
                     f"{p.get('edge_broken', 0)} | {sum(p.values())} |")
        L.append("")
    L += ["**Not done: comparison with Packard's published figures.** The plan asks to re-derive Packard-style "
          "figures as a sanity check. The table above is the re-derivation; Packard's own numbers (Packard 1974, "
          "*Minoan Linear A*) were not available in the session that built this report, so the comparison is open. "
          "It must be made on the full corpus counts in the book against a full-corpus run, or it will differ "
          "simply because the held-out documents are missing here.", "",
          "## Length of multi-sign groups", "",
          "| Signs | " + " | ".join(f"{s} all | {s} complete" for s in src) + " |", "|---|" + "---|---|" * len(src)]
    all_len = sorted({int(k) for s in src for k in P[s]["group_length"]})
    for n in all_len:
        L.append(f"| {n} | " + " | ".join(f"{P[s]['group_length'].get(str(n), 0)} | "
                                          f"{P[s]['group_length_complete'].get(str(n), 0)}" for s in src) + " |")
    for field, title in (("by_support", "support type"), ("by_register", "register"), ("by_site", "site")):
        L += ["", f"## By {title}", "", "Documents / sign-groups / identified sign tokens.", "",
              f"| {title.capitalize()} | " + " | ".join(src) + " |", "|---|" + "---|" * len(src)]
        keys = sorted({k for s in src for k in P[s][field]},
                      key=lambda k: (-max(P[s][field].get(k, {}).get("identified_tokens", 0) for s in src), k))
        small = [k for k in keys if max(P[s][field].get(k, {}).get("documents", 0) for s in src) < 5]
        for k in [k for k in keys if k not in small]:
            L.append(f"| {k} | " + " | ".join(
                "{documents} / {sign_groups} / {identified_tokens}".format(**P[s][field][k]) if k in P[s][field] else "—"
                for s in src) + " |")
        if small:
            L.append(f"| {len(small)} others with fewer than five documents | " + " | ".join(
                "{} / {} / {}".format(*(sum(P[s][field].get(k, {}).get(f, 0) for k in small)
                                        for f in ("documents", "sign_groups", "identified_tokens"))) for s in src) + " |")
    L += ["", "## By period, as each source gives it", "",
          "Period labels are not normalised across sources; documents per label.", ""]
    for s in src:
        L.append(f"- **{s}:** " + "; ".join(f"{k} {v}" for k, v in sorted(P[s]["by_period_as_given"].items(),
                                                                         key=lambda kv: (-kv[1], kv[0]))))
    L += ["", "## Limits", "",
          "- Training split only. Totals are smaller than any published full-corpus figure by construction.",
          "- The three sources all derive from GORILA, and lineara.xyz from Younger's earlier pages (A1.9). "
          "Agreement between columns is not independent confirmation.",
          "- lineara.xyz has no sign roles and incomplete damage marking; its position counts include logograms "
          "written inside words and treat unmarked breaks as intact.",
          "- Word division is each source's own. Where sources divide words differently, lengths and positions differ.",
          "- Sign variants are merged by base ID. An analysis that needs variants reads the JSON (`sign_frequency` "
          "is by base ID too; variants need a rerun with a different key).", ""]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--witnesses", type=Path, default=load.WITNESSES)
    ap.add_argument("--allow-partial", action="store_true",
                    help="accept a witnesses file that differs from the release (e.g. built without Younger); "
                         "the report is stamped PARTIAL BUILD")
    ap.add_argument("--n", type=int, default=N_RESAMPLES)
    args = ap.parse_args(argv)
    b = build(args.witnesses, args.allow_partial, args.n)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(b, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render(b), encoding="utf-8")
    print(json.dumps({"partial_build": b["partial_build"], "sources": b["sources_present"],
                      "training_documents_with_a_witness": b["training_documents_with_a_witness"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
