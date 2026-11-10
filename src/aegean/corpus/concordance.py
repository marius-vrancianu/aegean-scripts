"""Cross-source document concordance (A1.6).

Groups the records of lineara.xyz, SigLA and Younger into document clusters
keyed by GORILA siglum, and computes the per-document facts the inclusion
rules need (docs/inclusion-rules.md). Nothing here decides inclusion; that is
`aegean.corpus.inclusion`.

Matching (`aegean.corpus.siglum`):
- sides (a, b, alpha...) belong to one document;
- angle brackets are ignored for matching (sources disagree on them);
- records sharing a numbered component are one cluster, because sources join
  fragments differently (SigLA "KH Wc 2059+frr", Younger "KH Wc 2059+2091+2092").
  A cluster may therefore hold several GORILA numbers; its key is the one most
  sources use, and all are kept as aliases;
- Younger lists some separate documents in one entry ("KH Wa 1003, 1004",
  "KH Wa 1006-1008"); the entry is attached to each of them, flagged shared.

Records whose ID does not parse are kept in `unmatched`, never dropped silently.
"""
from __future__ import annotations

import collections
from dataclasses import asdict, dataclass, field
from pathlib import Path

from aegean.corpus import lineara, sigla, siglum, younger
from aegean.corpus.heldout import load_heldout

REPO = Path(__file__).resolve().parents[3]
INPUTS = {
    "lineara.xyz": REPO / "data/raw/lineara.xyz/9c81beba669a/LinearAInscriptions.js",
    "sigla": REPO / "data/raw/sigla/0c4ef69f5de4/database.js",
    "younger": REPO / "data/raw/younger/academia-2024/Linear_A_Texts_in_phonetic_transcription.pdf",
}

# GORILA series -> support class and register (GORILA's own classification:
# W = clay sealing documents, Z = inscriptions on other objects; no series = tablet).
SERIES_SUPPORT = {
    None: ("tablet", "administrative"),
    "Wa": ("nodule", "administrative"), "Wb": ("sealing", "administrative"),
    "Wc": ("roundel", "administrative"), "Wd": ("other_sealing", "administrative"),
    "We": ("other_sealing", "administrative"), "Wf": ("other_sealing", "administrative"),
    "Wg": ("other_sealing", "administrative"), "Ws": ("other_sealing", "administrative"),
    "Wy": ("other_sealing", "administrative"),
    "Za": ("stone_vessel", "non_administrative"), "Zb": ("clay_vessel", "non_administrative"),
    "Zc": ("inked", "non_administrative"), "Zd": ("graffito", "non_administrative"),
    "Ze": ("architecture", "non_administrative"), "Zf": ("metal_object", "non_administrative"),
    "Zg": ("stone_object", "non_administrative"),
}
ALIASES = REPO / "data/concordance/aliases.tsv"
# Site prefixes outside Crete, checked against the sources' site names (2026-11-10):
# THE Thera, MIL Miletos, MY Mycenae, KY Kythera, SAM / SA Samothrace (SA is the
# older prefix; Younger: "SAM We 4, formerly SA We 2"), TRO Troy, TEL Tel Haror,
# TI Tiryns, ARG Argos (Younger; lineara.xyz gives "Arkhalkhori": an A1.9 item).
# Not off Crete: SE = Selakanos, LACH = Larani (lineara.xyz site names).
OFF_CRETE = {"THE", "MIL", "MY", "KY", "SAM", "SA", "TRO", "TEL", "TI", "ARG"}


@dataclass
class SourceRecord:
    source: str
    source_id: str
    side: str | None
    shared_entry: bool = False  # one Younger entry covering several documents
    # content counts (L0 where the source allows; Younger counts are L1-based)
    signs: int = 0  # identified signs (syllabograms, logograms, composites)
    unidentified: int = 0
    numerals: int = 0  # numeral tokens / cells
    fractions: int = 0
    site_name: str = ""
    period: str = ""
    support_text: str = ""


@dataclass
class DocCluster:
    key: str
    aliases: list[str]
    site: str
    series: str | None
    support: str
    register: str
    off_crete: bool
    lost: bool  # angle-bracketed in at least one source
    flags: list[str]
    records: list[SourceRecord] = field(default_factory=list)

    @property
    def sources(self) -> list[str]:
        return sorted({r.source for r in self.records})

    @property
    def max_signs(self) -> int:
        """Largest identified-sign count over sources, summing sides within a source."""
        per = collections.Counter()
        for r in self.records:
            per[r.source] += r.signs
        return max(per.values(), default=0)

    @property
    def max_numerals(self) -> int:
        per = collections.Counter()
        for r in self.records:
            per[r.source] += r.numerals
        return max(per.values(), default=0)

    def to_dict(self) -> dict:
        d = asdict(self)
        d.update(sources=self.sources, max_signs=self.max_signs, max_numerals=self.max_numerals)
        return d


# --- per-source content counts ----------------------------------------------------

def _lineara_records(path: Path) -> list[SourceRecord]:
    held = load_heldout().get("lineara.xyz", set())
    out = []
    for d in lineara.load_documents(path, held):
        toks = [t for ln in d.lines for t in ln]
        out.append(SourceRecord(
            "lineara.xyz", d.id, None,
            signs=sum(len(t.signs) for t in toks),
            numerals=sum(1 for t in toks if t.value is not None),
            fractions=sum(len(t.fractions) for t in toks),
            site_name=d.site, period=d.period, support_text=d.support,
        ))
    return out


def _sigla_records(path: Path) -> list[SourceRecord]:
    out = []
    for d in sigla.load_documents(path):
        att = [a for a in d.attestations if not a.hidden]
        out.append(SourceRecord(
            "sigla", d.id, None,
            signs=sum(1 for a in att if a.sign_id and a.sign_class not in ("fraction", "punctuation")),
            unidentified=sum(1 for a in att if a.sign_id is None),
            numerals=sum(1 for a in att if a.sign_id == "AAP800"),
            fractions=sum(1 for a in att if a.sign_class == "fraction"),
            site_name=d.site, period=d.period or "", support_text=d.support,
        ))
    return out


def _younger_records(path: Path) -> list[tuple[SourceRecord, list[str]]]:
    """(record, all sigla the entry covers)."""
    out = []
    for d in younger.load_documents(path):
        signs = [s for r in d.rows for g in r.statement for s in g.signs]
        rec = SourceRecord(
            "younger", d.id, None,
            signs=sum(1 for s in signs if not s.unidentified) + sum(1 for r in d.rows if r.logogram),
            unidentified=sum(1 for s in signs if s.unidentified),
            numerals=sum(1 for r in d.rows if r.number),
            fractions=sum(1 for r in d.rows if r.fraction),
            period="", support_text=d.header[:80],
        )
        out.append((rec, [d.id] + d.joint_ids))
    return out


def load_aliases(path: Path = ALIASES) -> dict[tuple[str, str], tuple[str, str]]:
    """{(source, source_id): (key, confidence)} from data/concordance/aliases.tsv."""
    out = {}
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    for l in lines[1:]:
        source, sid, key, conf, *_ = l.split("\t")
        out[(source, sid)] = (key, conf)
    return out


# --- clustering ---------------------------------------------------------------------

class _UF:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def build(inputs: dict[str, Path] = INPUTS) -> tuple[list[DocCluster], list[SourceRecord]]:
    """(clusters, unmatched records). Held-out documents are excluded by every reader."""
    entries: list[tuple[SourceRecord, siglum.Siglum]] = []
    unmatched: list[SourceRecord] = []
    raw: list[tuple[SourceRecord, list[str]]] = []
    if inputs.get("lineara.xyz") and inputs["lineara.xyz"].exists():
        raw += [(r, [r.source_id]) for r in _lineara_records(inputs["lineara.xyz"])]
    if inputs.get("sigla") and inputs["sigla"].exists():
        raw += [(r, [r.source_id]) for r in _sigla_records(inputs["sigla"])]
    if inputs.get("younger") and inputs["younger"].exists():
        raw += _younger_records(inputs["younger"])
    alias = load_aliases()
    for rec, ids in raw:
        parsed = []
        for i in ids:
            a = alias.get((rec.source, i))
            if a:
                key, conf = a
                parsed.append(siglum.from_label(key, ("alias",) + (("id_unresolved",) if conf == "unresolved" else ())))
            else:
                parsed.append(siglum.parse(i))
        if any(p is None for p in parsed):
            unmatched.append(rec)
            continue
        for k, p in enumerate(parsed):
            r = rec if len(parsed) == 1 else SourceRecord(**{**asdict(rec), "shared_entry": True,
                                                              "source_id": ids[k] if k else rec.source_id})
            r.side = p.side
            entries.append((r, p))

    uf = _UF()
    for _, p in entries:
        comps = [c.replace("<", "").replace(">", "") for c in p.components]
        for c in comps[1:]:
            uf.union(comps[0], c)
        uf.find(comps[0])
    groups: dict[str, list[tuple[SourceRecord, siglum.Siglum]]] = collections.defaultdict(list)
    for r, p in entries:
        groups[uf.find(p.components[0].replace("<", "").replace(">", ""))].append((r, p))

    clusters = []
    for _, members in sorted(groups.items()):
        keys = collections.Counter(p.match_key for _, p in members)
        by_src = collections.defaultdict(set)
        for r, p in members:
            by_src[p.match_key].add(r.source)
        # Most sources first; on a tie the longer key (the full join, as edited) wins.
        key = max(keys, key=lambda k: (len(by_src[k]), keys[k], len(k)))
        p0 = next(p for _, p in members if p.match_key == key)
        support, register = SERIES_SUPPORT.get(p0.series, ("unknown", "unknown"))
        flags = sorted({f for _, p in members for f in p.flags})
        if len(keys) > 1:
            flags.append("join_or_key_differs")
        clusters.append(DocCluster(
            key=key, aliases=sorted(set(keys) - {key}), site=p0.site, series=p0.series,
            support=support, register=register, off_crete=p0.site in OFF_CRETE,
            lost=any(p.lost for _, p in members), flags=flags,
            records=[r for r, _ in members],
        ))
    return clusters, unmatched
