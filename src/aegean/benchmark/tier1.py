"""Tier 1 of the benchmark: false-positive rates of a lexical-matching method (A5.17). Layer: L1.

  python -m aegean.benchmark.tier1 --method M1 --lexicon hebrew-strong-verbs --protocol H-A5-01
  python -m aegean.benchmark.tier1 --method M1 --lexicon-file claim.txt --rules claim-rules.json --protocol H-A5-NN

The second form runs a third-party claim: its lexicon as a file of forms and
its licences as an M1 rules file (`aegean.benchmark.m1.M1Rules.from_json`).

Protocol: hypotheses/H-A5-01.md. Do not run this on Linear A for a (method,
lexicon) pair that has no merged hypothesis file (CLAUDE.md rule 3); the
hypothesis ID is written into the output.

What is computed
- **Hit rate** of an input under a lexicon: the share of its distinct,
  eligible sign-groups for which the method returns a match.
- **False-positive rate**: the mean hit rate under matched pseudo-lexicons
  (`aegean.benchmark.nulls.matched_lexicon`). No language stands behind such
  a lexicon, so every one of those matches is false.
- **Excess**: real-lexicon hit rate minus the false-positive rate.
- **Test 1** (real lexicon against noise): p1 = (1 + number of pseudo-lexicons
  whose hit rate is >= the real one) / (K + 1), one-sided.
- **Test 2** (Linear A against the control): the excess on Linear A minus the
  excess on Linear B words of known Greek meaning, the control re-weighted to
  Linear A's length distribution. p2 ranks that difference among the same
  difference for each pseudo-lexicon taken in turn as if it were the real
  one. A lexicon that is merely more or less permissive than the null shifts
  both excesses alike, and the difference removes it.
- **Outcome**: A, B or C from p1 and p2 (`label`).
- Secondary, descriptive: the Finding 001 null, per source, by length,
  lexicon-size sensitivity, random sign strings, permissiveness, and
  resampling intervals (A1.14).

Inputs. The primary Linear A input is one reading per document
(`resample.primary_reading`, source order SigLA, lineara.xyz, Younger), on
the training split. The three sources are also reported separately.

Writes experiments/A5.17/results/<method>-<lexicon>.json and .md (generated).
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

from aegean.benchmark import inputs, lexicons, nulls
from aegean.benchmark.interface import DOF_ITEMS, Lexicon, Method, SignGroup
from aegean.benchmark.m1 import M1, M1Rules
from aegean.corpus import load, resample

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "experiments/A5.17/results"
SOURCES = ("sigla", "lineara.xyz", "younger")
SOURCE_ORDER = ("sigla", "lineara.xyz", "younger")  # as in the A1.11 baseline report

# Protocol constants (hypotheses/H-A5-01.md). Changing one is a new protocol, not an option.
ALPHA = 0.05
N_NULL = 1000
SEED_NULL = 20261114
SEED_NULL_F001 = 20261118
SEED_STRINGS = 20261116
SEED_SIZE = 20261117
SEED_RESAMPLE = 20261115
N_RESAMPLE = 1000
P_DOUBT = 0.5
N_STRINGS = 20
SIZE_FACTORS = (0.5, 1.0, 2.0, 4.0)
N_SIZE = 20
LENGTH_BINS = (2, 3, 4, 5)  # 5 means 5 or more

METHODS = {"M1": M1}


# ---- core ------------------------------------------------------------------------------------

def hit_rate(method: Method, groups: list[SignGroup], prepared: Any) -> float:
    """Share of the eligible sign-groups that match. NaN if none is eligible."""
    el = [g for g in groups if method.eligible(g)]
    return sum(method.hits(el, prepared)) / len(el) if el else float("nan")


def matched_lexicons(real: Lexicon, method: Method, n: int, seed: int) -> list[Lexicon]:
    """n matched pseudo-lexicons (the decision null) from one seeded stream, in order."""
    rng = random.Random(seed)
    return [nulls.matched_lexicon(real, method, rng, i) for i in range(n)]


def null_lexicons(real: Lexicon, n: int, seed: int, size_factor: float = 1.0) -> list[Lexicon]:
    """n Finding 001 pseudo-lexicons (descriptive null) from one seeded stream, in order."""
    rng = random.Random(seed)
    return [nulls.pseudo_lexicon(real, rng, size_factor, i) for i in range(n)]


def compare(real: float, null: list[float]) -> dict[str, float]:
    """A real-lexicon hit rate against the hit rates under pseudo-lexicons."""
    s = sorted(null)
    k = len(s)
    return {
        "real": real,
        "false_positive_rate": statistics.fmean(s),
        "null_sd": statistics.stdev(s) if k > 1 else float("nan"),
        "null_low": resample.quantile(s, 0.025),
        "null_high": resample.quantile(s, 0.975),
        "null_min": s[0],
        "null_max": s[-1],
        "excess": real - statistics.fmean(s),
        "p": (1 + sum(x >= real for x in s)) / (k + 1),
        "p_lower": (1 + sum(x <= real for x in s)) / (k + 1),
        "n_null": k,
    }


def length_bin(g: SignGroup) -> int:
    return min(len(g), LENGTH_BINS[-1])


class HitTable:
    """Which sign-groups match under the real lexicon and under each pseudo-lexicon, as bit masks.

    Built once over a universe of eligible sign-groups; any subset's hit rates are then popcounts.
    """

    def __init__(self, method: Method, universe: list[SignGroup], real: Lexicon, null: list[Lexicon]) -> None:
        self.groups = sorted({g for g in universe if method.eligible(g)})
        self.index = {g: i for i, g in enumerate(self.groups)}
        self.real = self._mask(method.hits(self.groups, method.prepare(real)))
        self.null = [self._mask(method.hits(self.groups, method.prepare(l))) for l in null]

    @staticmethod
    def _mask(bits: list[bool]) -> int:
        m = 0
        for i, b in enumerate(bits):
            if b:
                m |= 1 << i
        return m

    def subset(self, groups) -> int:
        m = 0
        for g in groups:
            i = self.index.get(g)
            if i is not None:
                m |= 1 << i
        return m

    def rates(self, groups) -> tuple[int, float, list[float]]:
        """(number of eligible groups, real-lexicon hit rate, hit rate under each pseudo-lexicon)."""
        sub = self.subset(groups)
        n = sub.bit_count()
        if not n:
            raise ValueError("no eligible sign-group in this input")
        return n, (sub & self.real).bit_count() / n, [(sub & m).bit_count() / n for m in self.null]

    def compare(self, groups) -> dict[str, float]:
        n, real, null = self.rates(groups)
        out = compare(real, null)
        out["n"] = n
        return out

    def bins(self, groups) -> dict[int, list[SignGroup]]:
        by = collections.defaultdict(list)
        for g in set(groups):
            if g in self.index:
                by[length_bin(g)].append(g)
        return dict(by)

    def by_length(self, groups) -> dict[str, dict[str, float]]:
        by = collections.defaultdict(list)
        for g in set(groups):
            if g in self.index:
                by[length_bin(g)].append(g)
        return {(f"{b}+" if b == LENGTH_BINS[-1] else str(b)): self.compare(gs) for b, gs in sorted(by.items())}


class Control:
    """The control's hit rates per length bin, so that they can be re-weighted to any Linear A input."""

    def __init__(self, table: HitTable, control: list[SignGroup]) -> None:
        self.by_bin = {b: table.rates(gs) for b, gs in table.bins(control).items()}

    def standardised(self, weights: dict[int, int]) -> tuple[float, list[float], list[int]]:
        """(real rate, rate under each pseudo-lexicon, bins used), weighted by `weights` (bin -> count).

        Direct standardisation. A bin the control lacks is left out and the weights are renormalised.
        """
        used = sorted(b for b in weights if b in self.by_bin and weights[b])
        if not used:
            raise ValueError("the control shares no length bin with the input")
        total = sum(weights[b] for b in used)
        real = sum(self.by_bin[b][1] * weights[b] for b in used) / total
        k = len(self.by_bin[used[0]][2])
        null = [sum(self.by_bin[b][2][i] * weights[b] for b in used) / total for i in range(k)]
        return real, null, used


def difference_test(table: HitTable, groups, control: Control) -> dict[str, Any]:
    """Test 2: excess on the input minus excess on the length-standardised control.

    Each pseudo-lexicon is scored in turn as if it were the real one, against the mean of the others;
    p2 is the share of them whose difference is at least the real lexicon's (one-sided).
    """
    n, real, null = table.rates(groups)
    weights = {b: len(gs) for b, gs in table.bins(groups).items()}
    c_real, c_null, used = control.standardised(weights)
    k = len(null)
    m, cm = statistics.fmean(null), statistics.fmean(c_null)
    d_real = (real - m) - (c_real - cm)
    loo = k / (k - 1)  # leave-one-out: x_i - mean(others) = (x_i - mean(all)) * k / (k - 1)
    d_null = [loo * ((null[i] - m) - (c_null[i] - cm)) for i in range(k)]
    return {"excess_linear_a": real - m, "excess_control": c_real - cm, "difference": d_real,
            "control_real_standardised": c_real, "control_false_positive_rate_standardised": cm,
            "null_low": resample.quantile(sorted(d_null), 0.025), "null_high": resample.quantile(sorted(d_null), 0.975),
            "p": (1 + sum(x >= d_real for x in d_null)) / (k + 1), "length_bins_used": used, "n_null": k}


def label(p1: float, p2: float, alpha: float = ALPHA) -> str:
    """The Tier 1 outcome for one (method, lexicon) pair (hypotheses/H-A5-01.md, decision rule)."""
    if p1 <= alpha and p2 <= alpha:
        return "C: above the random-lexicon null, and more so than on the Greek control"
    if p1 > alpha and p2 > alpha:
        return "A: no better than a random lexicon"
    if p1 <= alpha:
        return "B: above the null, but no more than on the Greek control"
    return "B: differs from the Greek control, but not above the null"


def bh_adjust(pvalues: list[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values, in the input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adj = [0.0] * m
    running = 1.0
    for rank, i in reversed(list(enumerate(order, 1))):
        running = min(running, pvalues[i] * m / rank)
        adj[i] = running
    return adj


def permissiveness(method: Method, groups: list[SignGroup], prepared: Any) -> dict[str, Any] | None:
    """How many readings the method allows per sign-group, and how much of the reading space the lexicon covers.

    Only for methods that expose `skeletons` (M1). The space is every string of the lexicon's letters at
    the lexicon's lengths.
    """
    if not hasattr(method, "skeletons"):
        return None
    counts = sorted(len(method.skeletons(g)) for g in groups if method.eligible(g))
    letters = sorted({c for f in prepared for c in f})
    lengths = sorted({len(f) for f in prepared})
    space = sum(len(letters) ** n for n in lengths)
    return {"readings_per_group_mean": statistics.fmean(counts), "readings_per_group_median": statistics.median(counts),
            "readings_per_group_max": counts[-1], "lexicon_forms_after_expansion": len(prepared),
            "reading_space": space, "share_of_reading_space_in_lexicon": len(prepared) / space,
            "letters": "".join(letters), "lengths": lengths}


# ---- the run ---------------------------------------------------------------------------------

def run(method: Method, real: Lexicon, witnesses: list[dict], control: list[SignGroup], *, protocol: str,
        n_null: int = N_NULL, n_resample: int = N_RESAMPLE, seed_null: int = SEED_NULL,
        seed_resample: int = SEED_RESAMPLE) -> dict:
    """The whole Tier 1 table for one (method, lexicon) pair. `witnesses` come from `aegean.corpus.load`."""
    corpus = resample.group(witnesses)
    primary = resample.primary_reading(corpus, SOURCE_ORDER)
    occ = {"primary": inputs.linear_a_groups(primary),
           **{s: inputs.linear_a_groups([w for w in witnesses if w["source"] == s]) for s in SOURCES}}
    sets = {k: inputs.unique([g for _, g in v]) for k, v in occ.items()}
    universe = [g for gs in sets.values() for g in gs]

    # The decision null (matched) and the Finding 001 null (descriptive), each over Linear A and the control.
    matched = matched_lexicons(real, method, n_null, seed_null)
    table, ctable = HitTable(method, universe, real, matched), HitTable(method, control, real, matched)
    f001 = null_lexicons(real, n_null, SEED_NULL_F001)
    table_f, ctable_f = HitTable(method, universe, real, f001), HitTable(method, control, real, f001)
    ctrl = Control(ctable, control)

    la = {k: table.compare(gs) for k, gs in sets.items() if table.subset(gs)}  # a source may have no documents
    if "primary" not in la:
        raise ValueError("no eligible Linear A sign-group")
    lb = ctable.compare(control)
    test2 = difference_test(table, sets["primary"], ctrl)
    p1, p2 = la["primary"]["p"], test2["p"]

    # Random sign strings: lengths of the primary sign-groups, sign frequencies of all eligible occurrences.
    el = [g for g in sets["primary"] if method.eligible(g)]
    pool = [s for _, g in occ["primary"] if method.eligible(g) for s in g]
    rng = random.Random(SEED_STRINGS)
    prepared = method.prepare(real)
    strings = [hit_rate(method, nulls.random_sign_strings([len(g) for g in el], pool, rng), prepared)
               for _ in range(N_STRINGS)]

    size = {}
    for f in SIZE_FACTORS:
        rates = [hit_rate(method, el, method.prepare(l)) for l in null_lexicons(real, N_SIZE, SEED_SIZE, f)]
        size[f"{f:g}"] = {"forms": int(len(real) * f), "mean": statistics.fmean(rates), "min": min(rates), "max": max(rates)}

    names = ("real", "false_positive_rate", "excess", "difference", "p1_at_most_alpha", "p2_at_most_alpha", "n")

    def statistic(ws: list[dict]) -> dict[str, float]:
        gs = [g for _, g in inputs.linear_a_groups(ws)]
        if not table.subset(gs):  # a draw with nothing to match; dropped from the intervals
            return {k: float("nan") for k in names}
        c, d = table.compare(gs), difference_test(table, gs, ctrl)
        return {"real": c["real"], "false_positive_rate": c["false_positive_rate"], "excess": c["excess"],
                "difference": d["difference"], "p1_at_most_alpha": float(c["p"] <= ALPHA),
                "p2_at_most_alpha": float(d["p"] <= ALPHA), "n": c["n"]}

    res = resample.run(statistic, corpus, source_order=SOURCE_ORDER, seed=seed_resample, n=n_resample, p_doubt=P_DOUBT)
    # Share of combined draws (bootstrap + reading) in which each test is below alpha.
    r_share = random.Random(f"{seed_resample}:share")
    draws = []
    for _ in range(n_resample):
        keys = resample.bootstrap_keys(corpus, r_share, resample.site_of)
        draws.append(statistic(resample.reading_draw(corpus, keys, r_share, P_DOUBT)))
    share = {k: statistics.fmean(d[k] for d in draws if d[k] == d[k]) for k in ("p1_at_most_alpha", "p2_at_most_alpha")}

    return {
        "protocol": protocol,
        "method": method.name,
        "layer": method.layer,
        "rules": method.rules.to_json() if hasattr(method, "rules") else None,
        "lexicon": {"name": real.name, "forms": len(real), "forms_after_expansion": len(prepared), **real.meta},
        "null_lexicons": {
            "matched": {"n": n_null, "seed": seed_null, "forms_after_expansion": len(prepared),
                        "forms_mean": statistics.fmean(len(l) for l in matched)},
            "finding_001": {"n": n_null, "seed": SEED_NULL_F001, "forms": len(real),
                            "forms_after_expansion_mean": statistics.fmean(len(method.prepare(l)) for l in f001)},
        },
        "params": {"alpha": ALPHA, "seed_strings": SEED_STRINGS, "seed_size": SEED_SIZE,
                   "seed_resample": seed_resample, "n_resample": n_resample, "p_doubt": P_DOUBT,
                   "source_order": list(SOURCE_ORDER), "split": "train"},
        "inputs": {k: {"occurrences": len(occ[k]), "distinct": len(sets[k]), "eligible": la[k]["n"] if k in la else 0,
                       "documents": len({d for d, _ in occ[k]})} for k in occ},
        "linear_a": la,
        "control": lb,
        "test1": {"p": p1, "excess": la["primary"]["excess"]},
        "test2": test2,
        "p_pair": max(p1, p2),
        "outcome": label(p1, p2),
        "linear_a_by_length": table.by_length(sets["primary"]),
        "control_by_length": ctable.by_length(control),
        "finding_001_null": {"linear_a": table_f.compare(sets["primary"]), "control": ctable_f.compare(control)},
        "random_sign_strings": {"reps": N_STRINGS, "mean": statistics.fmean(strings), "min": min(strings),
                                "max": max(strings), "real_sign_groups": la["primary"]["real"]},
        "lexicon_size": size,
        "permissiveness": permissiveness(method, el, prepared),
        "degrees_of_freedom": method.degrees_of_freedom(),
        "resampling": {"estimate": res["estimate"], "reading": res["reading"], "bootstrap": res["bootstrap"],
                       "both": res["both"], "params": res["params"], "share_of_draws": share},
    }


# ---- report ----------------------------------------------------------------------------------

def _row(name: str, c: dict) -> str:
    return (f"| {name} | {c['n']} | {c['real']:.3f} | {c['false_positive_rate']:.3f} "
            f"({c['null_low']:.3f}–{c['null_high']:.3f}) | {c['excess']:+.3f} | {c['p']:.4f} |")


def report(r: dict, provenance: dict) -> str:
    la, lb, rs, t2, nl = r["linear_a"], r["control"], r["resampling"], r["test2"], r["null_lexicons"]
    head = ("| Input | Sign-groups | Real lexicon | False-positive rate (95% of pseudo-lexicons) | Excess | p |\n"
            "|---|---|---|---|---|---|")
    names = {"primary": "Linear A, one reading per document (primary)", "sigla": "Linear A, SigLA",
             "lineara.xyz": "Linear A, lineara.xyz", "younger": "Linear A, Younger (non-HT)"}
    control_name = "Linear B words of known Greek meaning (control)"
    lines = [
        f"# Tier 1 false-positive table: {r['method']} × {r['lexicon']['name']}",
        "",
        "Generated by `python -m aegean.benchmark.tier1`; do not edit. Protocol: "
        f"`hypotheses/{r['protocol']}.md`. Layer: {r['layer']}.",
        "",
        f"- **Corpus:** {provenance['corpus']} @ `{provenance['commit']}`, training split.",
        f"- **Lexicon:** {r['lexicon']['name']}, {r['lexicon']['forms']} forms "
        f"({r['lexicon']['forms_after_expansion']} after the method's lexicon-side licences).",
        f"- **Matched pseudo-lexicons:** {nl['matched']['n']}, seed {nl['matched']['seed']}; each has "
        f"{nl['matched']['forms_after_expansion']} forms after expansion ({nl['matched']['forms_mean']:.0f} before, on average).",
        "",
        f"## Outcome: {r['outcome']}",
        "",
        f"- **Test 1** (real lexicon against matched pseudo-lexicons, Linear A): excess {r['test1']['excess']:+.3f}, "
        f"p1 = {r['test1']['p']:.4f}.",
        f"- **Test 2** (Linear A against the Greek control): excess on Linear A {t2['excess_linear_a']:+.3f}, on the "
        f"control at Linear A's lengths {t2['excess_control']:+.3f}; difference {t2['difference']:+.3f} "
        f"(95% of pseudo-lexicons: {t2['null_low']:+.3f} to {t2['null_high']:+.3f}), p2 = {t2['p']:.4f}.",
        f"- p for the pair (the larger of the two): {r['p_pair']:.4f}; α = {r['params']['alpha']}.",
        "",
        "Hit rate = share of distinct, eligible sign-groups with a match. False-positive rate = mean hit rate "
        "under matched pseudo-lexicons (no language behind them). "
        "p = share of pseudo-lexicons that match at least as often as the real lexicon (one-sided).",
        "",
        head,
        *[_row(names[k], la[k]) for k in ("primary", *SOURCES) if k in la],
        _row(control_name, lb),
        "",
        "The decision uses the primary row and the control only. The per-source rows are descriptive.",
        "",
        "## By length (primary input and control)",
        "",
        "| Signs | Linear A n | real | false-positive rate | Linear B n | real | false-positive rate |",
        "|---|---|---|---|---|---|---|",
    ]
    cell = lambda x: f"{x['n']} | {x['real']:.3f} | {x['false_positive_rate']:.3f}" if x else "– | – | –"
    for b in sorted(set(r["linear_a_by_length"]) | set(r["control_by_length"])):
        lines.append(f"| {b} | {cell(r['linear_a_by_length'].get(b))} | {cell(r['control_by_length'].get(b))} |")
    f1 = r["finding_001_null"]
    lines += [
        "",
        "## The Finding 001 null (descriptive)",
        "",
        f"Pseudo-lexicons with the real lexicon's number of forms before expansion ({nl['finding_001']['forms']}); "
        f"after expansion they average {nl['finding_001']['forms_after_expansion_mean']:.0f} forms against the real "
        f"lexicon's {r['lexicon']['forms_after_expansion']}, so they are not size-matched as the method sees them.",
        "",
        head,
        _row(names["primary"], f1["linear_a"]),
        _row(control_name, f1["control"]),
        "",
        "## Sensitivity to readings and to which documents survive (A1.14)",
        "",
        f"{rs['params']['n']} draws, seed {rs['params']['seed']}, p_doubt {rs['params']['p_doubt']}. "
        "Intervals are 95% of draws; they describe sensitivity, not confidence in a property of the language.",
        "",
        "| Quantity | Estimate | Reading draws | Document bootstrap | Both |",
        "|---|---|---|---|---|",
    ]
    for k, nm, signed in (("real", "Real-lexicon hit rate", False), ("false_positive_rate", "False-positive rate", False),
                          ("excess", "Excess (test 1)", True), ("difference", "Difference from control (test 2)", True)):
        fmt = (lambda x: f"{x:+.3f}") if signed else (lambda x: f"{x:.3f}")
        iv = lambda t: f"{fmt(rs[t][k]['low'])} to {fmt(rs[t][k]['high'])}"
        lines.append(f"| {nm} | {fmt(rs['estimate'][k])} | {iv('reading')} | {iv('bootstrap')} | {iv('both')} |")
    ss, pm, sh = r["random_sign_strings"], r["permissiveness"], rs["share_of_draws"]
    lines += [
        "",
        f"Share of combined draws with p1 ≤ α: {sh['p1_at_most_alpha']:.3f}; with p2 ≤ α: {sh['p2_at_most_alpha']:.3f}.",
        "",
        "## Lexicon size (Finding 001 pseudo-lexicons, primary input)",
        "",
        "| Size × real | Forms | Mean hit rate | Range |",
        "|---|---|---|---|",
        *[f"| {k} | {v['forms']} | {v['mean']:.3f} | {v['min']:.3f}–{v['max']:.3f} |" for k, v in r["lexicon_size"].items()],
        "",
        "## Random sign strings (descriptive)",
        "",
        f"Real sign-groups {ss['real_sign_groups']:.3f}; random strings of the same lengths and sign frequencies "
        f"{ss['mean']:.3f} ({ss['min']:.3f}–{ss['max']:.3f}, {ss['reps']} repetitions), real lexicon. "
        "This compares sign-groups with noise, not lexicons, and decides nothing about a language.",
        "",
        "## Degrees of freedom (docs/guardrails.md, item 3)",
        "",
    ]
    if pm:
        lines += [f"- Readings per sign-group: mean {pm['readings_per_group_mean']:.1f}, median "
                  f"{pm['readings_per_group_median']:g}, maximum {pm['readings_per_group_max']}.",
                  f"- The expanded lexicon holds {pm['lexicon_forms_after_expansion']} of the {pm['reading_space']} "
                  f"possible forms ({pm['share_of_reading_space_in_lexicon']:.1%}; letters {pm['letters']}, "
                  f"lengths {pm['lengths']})."]
    for item in DOF_ITEMS:
        lines.append(f"- **{item.replace('_', ' ')}:** `{json.dumps(r['degrees_of_freedom'].get(item), ensure_ascii=False)}`")
    return "\n".join(lines) + "\n"


def provenance() -> dict:
    manifest = json.loads(load.RELEASE_MANIFEST.read_text(encoding="utf-8"))
    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {"corpus": manifest.get("release") or manifest.get("tag") or "corpus-v1.0", "commit": commit or "unknown"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", choices=sorted(METHODS), default="M1")
    ap.add_argument("--rules", type=Path, help="JSON file of method rules (M1: see M1Rules.from_json)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--lexicon", choices=sorted(lexicons.REGISTRY))
    g.add_argument("--lexicon-file", type=Path, help="text file, one form per line")
    ap.add_argument("--protocol", required=True, metavar="H-A5-NN", help="merged hypothesis file this run belongs to")
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    args = ap.parse_args(argv)
    if not load.HYPOTHESIS_ID_RE.fullmatch(args.protocol) or not (REPO / f"hypotheses/{args.protocol}.md").is_file():
        print(f"REFUSED: hypotheses/{args.protocol}.md does not exist; register the run first (CLAUDE.md rule 3)",
              file=sys.stderr)
        return 2
    method = METHODS[args.method](M1Rules.from_json(args.rules)) if args.rules else METHODS[args.method]()
    real = lexicons.REGISTRY[args.lexicon]() if args.lexicon else lexicons.from_file(args.lexicon_file)
    control, control_meta = inputs.linear_b_control()
    r = run(method, real, load.witnesses(), control, protocol=args.protocol)
    r["control_source"] = control_meta
    r["provenance"] = provenance()
    args.out.mkdir(parents=True, exist_ok=True)
    stem = f"{method.name}-{real.name}"
    (args.out / f"{stem}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (args.out / f"{stem}.md").write_text(report(r, r["provenance"]), encoding="utf-8")
    print(f"{stem}: {r['outcome']}  (wrote {args.out / (stem + '.md')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
