"""Resampling harness (A1.14; plan §0.7). Layer: whatever the statistic reads (normally L0).

Runs one analysis many times to show how far its result depends on (a) which
reading of a doubtful or disputed sign is taken and (b) which documents happen
to survive. It returns intervals to report beside the point estimate.

    from aegean.corpus import load, resample
    corpus = resample.group(load.witnesses())
    r = resample.run(my_statistic, corpus, source_order=("sigla", "lineara.xyz", "younger"), seed=1)

`my_statistic` takes a list of witness dicts (docs/schema.md) and returns a
number or a {name: number} dict. It must not care which source a witness is
from, because every draw mixes sources.

The two kinds of variation
--------------------------
(a) **Reading draws.** The sources are never merged (docs/schema.md), so the
    attested readings of a document are its witnesses, one set per source. A
    reading draw picks, for each document independently, one of the sources
    that has it, with equal probability, and uses that source's witnesses.
    Inside the chosen witnesses, every sign the source marks as doubtful is
    then, with probability `p_doubt`, replaced by an unidentified sign.
    - A disputed sign therefore takes each attested reading in turn, but the
      disputed signs of one document move together (one editor's reading at a
      time). No draw contains a combination of readings that no source has.
    - `p_doubt` is a convention, not a measurement: nobody knows how often a
      doubtful reading is wrong. It is recorded in the output.
(b) **Document bootstrap.** Documents are drawn with replacement inside each
    stratum (the site, by default), keeping each stratum's size. A statistic
    that rests on two or three documents shows a wide interval here.
(c) **Both**: a bootstrap sample with a fresh reading draw for each drawn
    document. This is the interval to report by default.

What this is not (CLAUDE.md rule 9): resampled corpora are thrown away after
the statistic is computed. They are never written out, never added to the
corpus and never counted as extra evidence. The intervals describe the
sensitivity of a result to reading and sampling; they are not confidence
intervals for a property of the Minoan language, because the documents are
not a random sample of what was written.

Every run takes an explicit seed, recorded in the output. Only
`random.Random.random()` is used, so results do not depend on the Python
version.
"""
from __future__ import annotations

import collections
import copy
import math
import random
from typing import Callable, Iterable

Witness = dict
Statistic = Callable[[list[Witness]], "float | int | dict[str, float | int]"]
Corpus = dict[str, dict[str, list[Witness]]]  # document key -> source -> witnesses (sides)


def group(witnesses: Iterable[Witness]) -> Corpus:
    """Witnesses (with `doc_key`, as aegean.corpus.load returns them) by document and source."""
    out: Corpus = collections.defaultdict(lambda: collections.defaultdict(list))
    for w in witnesses:
        out[w["doc_key"]][w["source"]].append(w)
    return {k: dict(v) for k, v in out.items()}


def site_of(doc_key: str) -> str:
    """The site prefix of a canonical document key ("HT 13" -> "HT", "KH Wc 2001" -> "KH")."""
    return doc_key.split(" ", 1)[0]


def _pick(rng: random.Random, n: int) -> int:
    return min(int(rng.random() * n), n - 1)


def _blank_doubtful(ws: list[Witness], rng: random.Random, p_doubt: float) -> list[Witness]:
    """Copies of the witnesses in which each doubtful sign is unidentified with probability p_doubt."""
    hits = [(a, b, c, d) for a, w in enumerate(ws) for b, ln in enumerate(w["lines"])
            for c, it in enumerate(ln["items"]) for d, t in enumerate(it["tokens"])
            if t.get("doubtful") and rng.random() < p_doubt]
    if not hits:
        return ws
    ws = copy.deepcopy(ws)
    for a, b, c, d in hits:
        t = ws[a]["lines"][b]["items"][c]["tokens"][d]
        t.update(sign_id=None, l1=None, unidentified=True, components=[])
        t.setdefault("flags", []).append("resample:doubtful_blanked")
    return ws


def primary_reading(corpus: Corpus, source_order: tuple[str, ...]) -> list[Witness]:
    """One source per document: the first in `source_order` that has it. The point estimate uses this."""
    out = []
    for key in sorted(corpus):
        src = next((s for s in source_order if s in corpus[key]), None)
        if src is None:
            raise ValueError(f"{key}: none of {source_order} has this document ({sorted(corpus[key])})")
        out += corpus[key][src]
    return out


def reading_draw(corpus: Corpus, keys: list[str], rng: random.Random, p_doubt: float) -> list[Witness]:
    out = []
    for key in keys:
        sources = sorted(corpus[key])
        out += _blank_doubtful(corpus[key][sources[_pick(rng, len(sources))]], rng, p_doubt)
    return out


def bootstrap_keys(corpus: Corpus, rng: random.Random, stratum: Callable[[str], str]) -> list[str]:
    by: dict[str, list[str]] = collections.defaultdict(list)
    for key in sorted(corpus):
        by[stratum(key)].append(key)
    return [ks[_pick(rng, len(ks))] for s in sorted(by) for ks in [by[s]] for _ in ks]


def _as_dict(value) -> dict[str, float]:
    return dict(value) if isinstance(value, dict) else {"value": value}


def quantile(sorted_values: list[float], q: float) -> float:
    """Linear-interpolation quantile of an already sorted list."""
    if not sorted_values:
        return math.nan
    pos = q * (len(sorted_values) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def _summary(draws: list[dict[str, float]], level: float) -> dict[str, dict]:
    out = {}
    for name in sorted({n for d in draws for n in d}):
        vals = sorted(d[name] for d in draws if name in d and not (isinstance(d[name], float) and math.isnan(d[name])))
        a = (1 - level) / 2
        out[name] = {"low": quantile(vals, a), "median": quantile(vals, 0.5), "high": quantile(vals, 1 - a),
                     "min": vals[0] if vals else math.nan, "max": vals[-1] if vals else math.nan, "n": len(vals)}
    return out


def run(statistic: Statistic, corpus: Corpus, *, source_order: tuple[str, ...], seed: int, n: int = 1000,
        p_doubt: float = 0.5, level: float = 0.95, stratum: Callable[[str], str] = site_of) -> dict:
    """Point estimate on the primary reading, and intervals over reading draws, bootstrap samples and both.

    Returns {"estimate": {name: value}, "reading": {name: {low, median, high, min, max, n}},
             "bootstrap": {...}, "both": {...}, "params": {...}}.
    "bootstrap" resamples documents but keeps the primary reading; "both" also redraws the reading.
    """
    if not corpus:
        raise ValueError("empty corpus")
    if not 0 <= p_doubt <= 1 or not 0 < level < 1 or n < 1:
        raise ValueError("p_doubt in [0, 1], level in (0, 1) and n >= 1 are required")
    keys = sorted(corpus)
    primary = {k: primary_reading({k: corpus[k]}, source_order) for k in keys}
    estimate = _as_dict(statistic([w for k in keys for w in primary[k]]))
    # Independent streams, so that changing n for one kind does not shift the others.
    r_read, r_boot, r_both = (random.Random(f"{seed}:{tag}") for tag in ("reading", "bootstrap", "both"))
    reading = [_as_dict(statistic(reading_draw(corpus, keys, r_read, p_doubt))) for _ in range(n)]
    boot = [_as_dict(statistic([w for k in bootstrap_keys(corpus, r_boot, stratum) for w in primary[k]]))
            for _ in range(n)]
    both = [_as_dict(statistic(reading_draw(corpus, bootstrap_keys(corpus, r_both, stratum), r_both, p_doubt)))
            for _ in range(n)]
    sources = collections.Counter(len(v) for v in corpus.values())
    return {
        "estimate": estimate,
        "reading": _summary(reading, level),
        "bootstrap": _summary(boot, level),
        "both": _summary(both, level),
        "params": {"seed": seed, "n": n, "p_doubt": p_doubt, "level": level, "source_order": list(source_order),
                   "stratum": getattr(stratum, "__name__", "custom"), "documents": len(keys),
                   "strata": len({stratum(k) for k in keys}),
                   "documents_by_number_of_sources": {str(k): v for k, v in sorted(sources.items())},
                   "doubtful_signs_in_primary_reading": sum(bool(t.get("doubtful")) for k in keys for w in primary[k]
                                                           for ln in w["lines"] for it in ln["items"]
                                                           for t in it["tokens"])},
    }
