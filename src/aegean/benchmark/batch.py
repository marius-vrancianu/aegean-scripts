"""The Tier 1 batches: registration check and the batch correction.

Two protocols exist. Each has its own batch, its own correction and its own
batch table; a pair belongs to exactly one protocol, named in its hypothesis file.

| Protocol | Decision null | Batch table |
|---|---|---|
| H-A5-01 (Part 1) | matched pseudo-lexicons (`nulls.matched_lexicon`) | `batch.md`, `batch.json` |
| H-A5-03 | length-stratified matched pseudo-lexicons (`nulls.stratified_matched_lexicon`) | `batch-H-A5-03.md`, `.json` |
| H-A5-09 | position-aware bigram-matched, length-stratified pseudo-lexicons (`nulls.positional_bigram_matched_lexicon`) | `batch-H-A5-09.md`, `.json` |

Everything else (inputs, tests, α, decision rule, Benjamini–Hochberg) is the same.

Two things the runner must not leave to whoever calls it:

1. **A run belongs to a merged hypothesis** (CLAUDE.md rule 3). `check_registered`
   accepts a hypothesis ID only if `hypotheses/<ID>.md` exists, is byte-identical
   to the file on `origin/main` (or `main`), and, unless it is itself a protocol
   file, names one protocol in a line `- **Protocol:** H-A5-01` (or H-A5-03). It
   returns that protocol.
2. **Outcome C is granted only after the batch correction.** The batch is every
   (method, lexicon) pair ever run under the protocol, failures included. Each
   run is one generated JSON file in `experiments/A5.17/results/`; `records`
   reads them all and `apply` gives each pair its Benjamini–Hochberg adjusted
   pair p and its final outcome:
   - A and the first two kinds of B are decided on the raw p1 and p2 alone;
   - a pair with p1 ≤ α and p2 ≤ α is C if its adjusted pair p is ≤ 0.05,
     and B (the third kind) otherwise. The correction never changes an A.

   The batch table is written to `batch.json` and `batch.md` beside the
   results. When adding a pair changes an earlier pair's label, the runner says
   so; the outcome file of the pair that caused it must record it.

The results files are the record of the batch. Deleting one would drop a pair
from the correction, so they are committed with the outcome, and a run never
overwrites another hypothesis's file.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

PROTOCOL = "H-A5-01"  # the first protocol; results files without a batch_protocol field belong to it
PROTOCOLS = {
    # "pairs": the only hypotheses a closed protocol still accepts (None = open). H-A5-03, Part 1, point 3
    # closes H-A5-01 to new pairs, so that no pair can be run under both nulls and the better result kept.
    "H-A5-01": {"null": "matched", "batch_stem": "batch", "pairs": {"H-A5-01", "H-A5-02"}},
    # H-A5-09 closes H-A5-03 to new pairs in turn (review of PR #55, M1): only its six registered pairs remain.
    "H-A5-03": {"null": "stratified", "batch_stem": "batch-H-A5-03",
                "pairs": {"H-A5-03", "H-A5-04", "H-A5-05", "H-A5-06", "H-A5-07", "H-A5-08"}},
    "H-A5-09": {"null": "posbigram", "batch_stem": "batch-H-A5-09", "pairs": None},
}
ALPHA = 0.05
Q = 0.05
MAX_PAIRS = 50  # H-A5-01, power check: beyond 50 pairs the smallest attainable p is no longer attainable after BH
BATCH_FILES = tuple(f"{v['batch_stem']}.json" for v in PROTOCOLS.values())
MAIN_REFS = ("origin/main", "main")
HYPOTHESIS_ID_RE = re.compile(r"H-A5-\d+")
PROTOCOL_LINE_RE = re.compile(r"^\s*[-*]?\s*\*\*Protocol:\*\*\s*`?(H-A5-\d+)`?", re.MULTILINE)

LABEL_A = "A: no better than a random lexicon"
LABEL_B1 = "B: above the null, but no more than on the Greek control"
LABEL_B2 = "B: differs from the Greek control, but not above the null"
LABEL_B3 = "B: passes both tests alone, but not after the batch correction"
LABEL_C = "C: above the random-lexicon null, and more so than on the Greek control"


class NotRegistered(RuntimeError):
    """The hypothesis named for a run is missing, not merged, changed since the merge, or not under the protocol."""


class BatchError(RuntimeError):
    """The batch cannot take this run (a pair already registered differently, or the batch is full)."""


# ---- registration ----------------------------------------------------------------------------

def _on_main(repo: Path, rel: str) -> bytes | None:
    found_ref = False
    for ref in MAIN_REFS:
        r = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{rel}"], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        if subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", ref], capture_output=True).returncode == 0:
            found_ref = True
    if not found_ref:
        raise NotRegistered(f"no {' or '.join(MAIN_REFS)} ref in {repo}: cannot check that the hypothesis is merged")
    return None


def check_registered(hypothesis_id: str, repo: Path) -> str:
    """The protocol a Tier 1 run of this hypothesis belongs to; NotRegistered if it may not be run."""
    if not isinstance(hypothesis_id, str) or not HYPOTHESIS_ID_RE.fullmatch(hypothesis_id):
        raise NotRegistered(f"not an A5 hypothesis ID (H-A5-<nn>): {hypothesis_id!r}")
    rel = f"hypotheses/{hypothesis_id}.md"
    path = repo / rel
    if not path.is_file():
        raise NotRegistered(f"{rel} does not exist: register the run first (CLAUDE.md rule 3)")
    merged = _on_main(repo, rel)
    if merged is None:
        raise NotRegistered(f"{rel} is not on main: a hypothesis is registered only once it is merged")
    if merged != path.read_bytes():
        raise NotRegistered(f"{rel} differs from the merged version on main")
    if hypothesis_id in PROTOCOLS:
        protocol = hypothesis_id
    else:
        cited = PROTOCOL_LINE_RE.findall(merged.decode("utf-8", errors="replace"))
        if len(cited) != 1 or cited[0] not in PROTOCOLS:
            raise NotRegistered(f"{rel} must name its protocol in one line '- **Protocol:** <one of "
                                f"{', '.join(PROTOCOLS)}>' (found {cited or 'none'})")
        protocol = cited[0]
    allowed = PROTOCOLS[protocol]["pairs"]
    if allowed is not None and hypothesis_id not in allowed:
        raise NotRegistered(f"protocol {protocol} is closed to new pairs (H-A5-03, Part 1, point 3); "
                            f"register {hypothesis_id} under an open protocol")
    return protocol


# ---- the batch -------------------------------------------------------------------------------

def pair_key(result: dict) -> str:
    """What makes two runs the same pair: method, its rules, and the lexicon's content."""
    lex = result["lexicon"]
    ident = {"method": result["method"], "rules": result.get("rules"), "lexicon": lex["name"],
             "lexicon_sha256": lex.get("sha256"), "forms": lex.get("forms")}
    return hashlib.sha256(json.dumps(ident, sort_keys=True).encode()).hexdigest()[:16]


def record(result: dict, stem: str) -> dict:
    return {"stem": stem, "hypothesis": result["protocol"], "method": result["method"],
            "lexicon": result["lexicon"]["name"], "pair_key": pair_key(result),
            "p1": result["test1"]["p"], "p2": result["test2"]["p"], "p_pair": max(result["test1"]["p"], result["test2"]["p"])}


def records(out_dir: Path, protocol: str = PROTOCOL) -> list[dict]:
    """One record per results file of `protocol` in the folder, sorted by hypothesis ID number."""
    out = []
    for p in sorted(Path(out_dir).glob("*.json")):
        if p.name in BATCH_FILES:
            continue
        r = json.loads(p.read_text(encoding="utf-8"))
        if r.get("batch_protocol", PROTOCOL) == protocol and "test1" in r:
            out.append(record(r, p.stem))
    return sorted(out, key=lambda x: int(x["hypothesis"].rsplit("-", 1)[1]))


def bh_adjust(pvalues: list[float]) -> list[float]:
    """Benjamini–Hochberg adjusted p-values, in the input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adj = [0.0] * m
    running = 1.0
    for rank, i in reversed(list(enumerate(order, 1))):
        running = min(running, pvalues[i] * m / rank)
        adj[i] = running
    return adj


def label(p1: float, p2: float, p_adjusted: float, alpha: float = ALPHA, q: float = Q) -> str:
    """The registered outcome from the raw p1, p2 and the batch-adjusted pair p."""
    if p1 > alpha and p2 > alpha:
        return LABEL_A
    if p1 <= alpha < p2:
        return LABEL_B1
    if p2 <= alpha < p1:
        return LABEL_B2
    return LABEL_C if p_adjusted <= q else LABEL_B3


def apply(recs: list[dict]) -> list[dict]:
    """The records with `p_adjusted` and `outcome` filled in."""
    if len(recs) > MAX_PAIRS:
        raise BatchError(f"{len(recs)} pairs: H-A5-01 allows at most {MAX_PAIRS}; a larger batch needs a new protocol")
    adj = bh_adjust([r["p_pair"] for r in recs])
    return [{**r, "p_adjusted": a, "outcome": label(r["p1"], r["p2"], a)} for r, a in zip(recs, adj)]


def admit(recs: list[dict], new: dict) -> list[dict]:
    """The batch with `new` added, or with its earlier run replaced (a repeated run of the same hypothesis).

    A hypothesis is one pair, and a pair is run under one hypothesis: a clash either way is a BatchError.
    """
    for r in recs:
        if r["hypothesis"] == new["hypothesis"] and r["pair_key"] != new["pair_key"]:
            raise BatchError(f"{new['hypothesis']} was run with a different pair ({r['stem']}); one hypothesis is one pair")
        if r["pair_key"] == new["pair_key"] and r["hypothesis"] != new["hypothesis"]:
            raise BatchError(f"this pair was already run under {r['hypothesis']} ({r['stem']}); a pair is run once")
        if r["stem"] == new["stem"] and r["hypothesis"] != new["hypothesis"]:
            raise BatchError(f"results file {r['stem']}.json belongs to {r['hypothesis']}")
    kept = [r for r in recs if r["hypothesis"] != new["hypothesis"]]
    return sorted(kept + [new], key=lambda x: int(x["hypothesis"].rsplit("-", 1)[1]))


def changes(previous: list[dict], current: list[dict]) -> list[str]:
    """Earlier pairs whose outcome differs between two batch tables."""
    before = {r["hypothesis"]: r["outcome"] for r in previous}
    return [f"{r['hypothesis']} ({r['stem']}): {before[r['hypothesis']]} → {r['outcome']}"
            for r in current if r["hypothesis"] in before and before[r["hypothesis"]] != r["outcome"]]


def stem_for(recs: list[dict], hypothesis: str, method: str, lexicon: str) -> str:
    """The results file name: the hypothesis's existing one, else `<hypothesis>-<method>-<lexicon>`."""
    for r in recs:
        if r["hypothesis"] == hypothesis:
            return r["stem"]
    return f"{hypothesis}-{method}-{lexicon}"


def report(table: list[dict], changed: list[str], protocol: str = PROTOCOL) -> str:
    where = "hypotheses/H-A5-01.md, Part 1" if protocol == "H-A5-01" else f"hypotheses/{protocol}.md"
    lines = [
        f"# Tier 1 batch ({where})",
        "",
        "Generated by `python -m aegean.benchmark.tier1`; do not edit. Every (method, lexicon) pair run under the "
        f"protocol, failures included. Benjamini–Hochberg at q = {Q} over the pair p-values (the larger of p1 and "
        f"p2). Outcome C needs p1 ≤ {ALPHA}, p2 ≤ {ALPHA} and an adjusted pair p ≤ {Q}.",
        "",
        "| Pair | Hypothesis | Method | Lexicon | p1 | p2 | Pair p | Adjusted | Outcome |",
        "|---|---|---|---|---|---|---|---|---|",
        *[f"| {i} | {r['hypothesis']} | {r['method']} | {r['lexicon']} | {r['p1']:.4f} | {r['p2']:.4f} | "
          f"{r['p_pair']:.4f} | {r['p_adjusted']:.4f} | {r['outcome']} |" for i, r in enumerate(table, 1)],
        "",
        f"{len(table)} pair{'s' if len(table) != 1 else ''} in the batch (at most {MAX_PAIRS}).",
    ]
    if changed:
        lines += ["", "**Outcomes changed by the latest run** (record this in that run's outcome file):", "",
                  *[f"- {c}" for c in changed]]
    return "\n".join(lines) + "\n"


def _previous(out_dir: Path, protocol: str) -> list[dict]:
    path = Path(out_dir) / f"{PROTOCOLS[protocol]['batch_stem']}.json"
    return json.loads(path.read_text(encoding="utf-8"))["pairs"] if path.exists() else []


def update(out_dir: Path, result: dict, stem: str, protocol: str = PROTOCOL) -> tuple[list[dict], list[str]]:
    """Add one run to its protocol's batch; returns the new table and the outcome changes it caused. Writes nothing."""
    table = apply(admit(records(out_dir, protocol), record(result, stem)))
    return table, changes(_previous(out_dir, protocol), table)


def write(out_dir: Path, table: list[dict], changed: list[str], protocol: str = PROTOCOL) -> None:
    out_dir, stem = Path(out_dir), PROTOCOLS[protocol]["batch_stem"]
    (out_dir / f"{stem}.json").write_text(json.dumps({"protocol": protocol, "q": Q, "pairs": table}, indent=1,
                                                     ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / f"{stem}.md").write_text(report(table, changed, protocol), encoding="utf-8")


def entry(table: list[dict], hypothesis: str) -> dict[str, Any]:
    """The run's own row and the batch size, for its results file."""
    row = next(r for r in table if r["hypothesis"] == hypothesis)
    return {"size": len(table), "q": Q, "p_adjusted": row["p_adjusted"], "outcome": row["outcome"]}


def main(argv: list[str] | None = None) -> int:
    """Rebuild batch.json and batch.md from the results files, without running anything.

      python -m aegean.benchmark.batch [--protocol H-A5-01] [--out experiments/A5.17/results]
    """
    import argparse
    import sys
    ap = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[3] / "experiments/A5.17/results")
    ap.add_argument("--protocol", choices=sorted(PROTOCOLS), default=PROTOCOL)
    args = ap.parse_args(argv)
    previous = _previous(args.out, args.protocol)
    try:
        table = apply(records(args.out, args.protocol))
    except BatchError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    changed = changes(previous, table)
    write(args.out, table, changed, args.protocol)
    for r in table:
        print(f"{r['hypothesis']}  {r['stem']}: pair p {r['p_pair']:.4f}, adjusted {r['p_adjusted']:.4f}, {r['outcome']}")
    for c in changed:
        print(f"OUTCOME CHANGED: {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
