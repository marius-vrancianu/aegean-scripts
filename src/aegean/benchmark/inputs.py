"""Inputs to the benchmark: Linear A sign-groups and the Linear B control words. Layer: L1.

Linear A
--------
Read through `aegean.corpus.load` only (training split by default). A
**sign-group for matching** is

- an item of kind `word` (not a logogram, numeral or fraction),
- of two or more signs, fraction signs removed,
- complete: neither edge marked broken, every sign identified.

Its signs are given as uniform L1 values (`Token.l1`, docs/layers.md): the
Unicode Linear B value of the sign, or "*" + number where there is none.
Finding 001 read lineara.xyz's `transliteratedWords` instead; that field is
value-converted and is not parsed any more (CLAUDE.md, data rules), so the
sign-group lists differ slightly from Finding 001's 696.

Whether a method can use a group (all values known to it) is the method's
`eligible`, not decided here.

The sources are never merged. `linear_a_groups` takes the witnesses of one
source, or of one reading per document (`aegean.corpus.resample`).

Linear B control (docs/guardrails.md item 2)
--------------------------------------------
Linear B words with an identified Greek counterpart, from the NeuroDecipher
data (Luo, Cao & Barzilay 2019; DATA_SOURCES.md): column 1 of
`linear_b-greek.cog`, converted sign by sign to the same Unicode Linear B
values. These are Greek words; a method that "finds" another language in
them is finding it in the wrong place.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

from aegean.benchmark.interface import SignGroup
from aegean.corpus.baseline import _edge_intact, _is_fraction

REPO = Path(__file__).resolve().parents[3]
ND_COMMIT = "480bad2487820e3737fecfdd108214efa769e34b"
ND_SHA256 = "0e8099cd9f02c36fc14599d9bc12836489816c0b1d17f471e723b98c978b10fa"
ND_COG = REPO / f"data/raw/neurodecipher/{ND_COMMIT[:12]}/linear_b-greek.cog"

_LB_NAME = re.compile(r"LINEAR B (?:SYLLABLE|SYMBOL) B(\d{3})(?: (.+))?$")


def linear_a_groups(witnesses: list[dict], min_signs: int = 2) -> list[tuple[str, SignGroup]]:
    """(document key, sign-group) for every complete multi-sign word in the witnesses, in corpus order."""
    out = []
    for w in witnesses:
        for ln in w["lines"]:
            for it in ln["items"]:
                if it["kind"] != "word":
                    continue
                toks = [t for t in it["tokens"] if not _is_fraction(t.get("sign_id"))]
                if len(toks) < min_signs or any(not t.get("l1") for t in toks):
                    continue
                if not (_edge_intact(it, toks[0], "left") and _edge_intact(it, toks[-1], "right")):
                    continue
                out.append((w.get("doc_key", ""), tuple(t["l1"].upper() for t in toks)))
    return out


def unique(groups: list[SignGroup]) -> list[SignGroup]:
    """Distinct sign-groups, sorted (the unit of the hit rate, as in Finding 001)."""
    return sorted(set(groups))


def linear_b_value(ch: str) -> str | None:
    """The Unicode Linear B value of one character ("KO"), "*18" for a valueless sign, None if not Linear B."""
    m = _LB_NAME.match(unicodedata.name(ch, ""))
    if not m:
        return None
    return m.group(2) if m.group(2) else f"*{int(m.group(1))}"


def parse_cog(text: str, min_signs: int = 2) -> tuple[list[SignGroup], dict]:
    """Sign-groups of the Linear B words that have a Greek counterpart, and counts of what was dropped."""
    rows = text.splitlines()
    if not rows or rows[0].split("\t")[:2] != ["linear_b", "greek"]:
        raise ValueError("not a NeuroDecipher linear_b-greek .cog file (header mismatch)")
    out, dropped = [], {"no_greek": 0, "non_linear_b_sign": 0, "too_short": 0}
    for row in rows[1:]:
        if not row.strip():
            continue
        lb, greek = row.split("\t")[:2]
        if greek.strip() in ("", "_"):
            dropped["no_greek"] += 1
            continue
        vals = [linear_b_value(c) for c in lb.strip()]
        if None in vals:
            dropped["non_linear_b_sign"] += 1
        elif len(vals) < min_signs:
            dropped["too_short"] += 1
        else:
            out.append(tuple(vals))
    return out, dropped


def linear_b_control(path: Path = ND_COG, verify_hash: bool = True) -> tuple[list[SignGroup], dict]:
    """The distinct Linear B control words and a record of their source."""
    if not path.exists():
        raise FileNotFoundError(f"{path} is not fetched; run python data/raw/neurodecipher/fetch.py")
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if verify_hash and got != ND_SHA256:
        raise RuntimeError(f"HASH MISMATCH for {path}: {got}, expected {ND_SHA256}")
    words, dropped = parse_cog(data.decode("utf-8"))
    return unique(words), {"source": "j-luo93/NeuroDecipher data/linear_b-greek.cog", "commit": ND_COMMIT,
                           "sha256": got, "rows_used": len(words), "distinct": len(set(words)), "dropped": dropped}
