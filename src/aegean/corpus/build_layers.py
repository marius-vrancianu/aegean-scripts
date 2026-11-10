"""Build all witnesses with layers L0 and L1 (A1.8).

  python -m aegean.corpus.build_layers

Writes data/processed/corpus-v1.0-pre/witnesses.jsonl (gitignored: it holds
source texts whose licences do not all allow redistribution) and MANIFEST.json
(committed: input hashes, counts, the Younger-vs-SigLA validation, output hash).
The release corpus-v1.0 is tagged at A1.12, after the held-out split.
"""
from __future__ import annotations

import collections
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from aegean.corpus import concordance, layers, lineara, schema, sigla, siglum, witnesses, younger
from aegean.corpus.document_list import PINNED, sha256
from aegean.corpus.heldout import load_heldout

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "data/processed/corpus-v1.0-pre"


def all_witnesses() -> tuple[list[schema.Witness], dict]:
    for src, path in concordance.INPUTS.items():
        if not path.exists():
            raise SystemExit(f"missing input {path}")
        if sha256(path) != PINNED[src]:
            raise SystemExit(f"HASH MISMATCH for {path}")
    sp = concordance.INPUTS["sigla"]
    ssigns = sigla.load_signs(sp)
    sd = {s.sign_id: s for s in ssigns}
    comp = layers.sigla_composites(ssigns)
    lw = [witnesses.from_lineara(d) for d in lineara.load_documents(concordance.INPUTS["lineara.xyz"],
                                                                       load_heldout().get("lineara.xyz", set()))]
    sw = [witnesses.from_sigla(d, sd) for d in sigla.load_documents(sp)]
    yw = [witnesses.from_younger(d) for d in younger.load_documents(concordance.INPUTS["younger"])]
    out = [layers.apply(w, comp) for w in lw + sw + yw]
    by_key = collections.defaultdict(list)
    for w in out:
        if w.source == "sigla":
            p = siglum.parse(w.source_id)
            by_key[p.match_key].append((p.side or "", w))
    pairs = []
    for w in out:
        if w.source == "younger" and (p := siglum.parse(w.source_id)) and p.match_key in by_key:
            pairs.append((w, [x for _, x in sorted(by_key[p.match_key], key=lambda z: z[0])]))
    val = layers.validate_against_sigla(pairs)
    return sorted(out, key=lambda w: (w.source, w.source_id, w.side or "")), {**val, "documents_paired": len(pairs)}


def build(out: Path = OUT) -> dict:
    ws, val = all_witnesses()
    errs = [(w.source, w.source_id, e) for w in ws for e in schema.validate(w)]
    if errs:
        raise SystemExit(f"{len(errs)} schema errors, e.g. {errs[:3]}")
    out.mkdir(parents=True, exist_ok=True)
    path = out / "witnesses.jsonl"
    path.write_text("".join(json.dumps(asdict(w), ensure_ascii=False, sort_keys=True) + "\n" for w in ws),
                    encoding="utf-8")
    toks = [(w.source, t) for w in ws for t in w.tokens()]
    by_src = collections.defaultdict(collections.Counter)
    for s, t in toks:
        c = by_src[s]
        c["tokens"] += 1
        c["l0_sign_id"] += t.sign_id is not None
        c["unidentified"] += t.unidentified
        c["l1"] += t.l1 is not None
    manifest = {
        "task": "A1.8",
        "schema_version": schema.SCHEMA_VERSION,
        "inputs": {s: {"path": str(p.relative_to(REPO)), "sha256": PINNED[s]} for s, p in concordance.INPUTS.items()},
        "witnesses": dict(collections.Counter(w.source for w in ws)),
        "tokens": {s: dict(c) for s, c in sorted(by_src.items())},
        "younger_vs_sigla": {k: val[k] for k in ("documents_paired", "aligned", "agree", "disagree")},
        "younger_extra_values": {k: list(v) for k, v in layers.YOUNGER_EXTRA.items()},
        "younger_extra_values_validation": {k: val["per_value"].get(k, {}) for k in layers.YOUNGER_EXTRA},
        "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "licence_note": "witnesses.jsonl is not committed: it holds lineara.xyz and Younger texts (no licence) and "
                        "SigLA data (CC BY-NC-SA 4.0). Rebuild it from the pinned inputs.",
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    m = build()
    print(json.dumps({k: m[k] for k in ("witnesses", "tokens", "younger_vs_sigla")}, indent=1))
