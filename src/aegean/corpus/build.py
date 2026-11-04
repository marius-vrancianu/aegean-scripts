"""Build a corpus release from pinned sources.

  python -m aegean.corpus.build --version corpus-v0.1

Writes data/processed/<version>/documents.jsonl (gitignored, regenerable) and
data/processed/<version>/MANIFEST.json (committed: input and output hashes,
counts). A release is reproducible if rebuilding gives the same output hash.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

from aegean.corpus import lineara
from aegean.corpus.heldout import load_heldout

REPO = Path(__file__).resolve().parents[3]

RELEASES = {
    "corpus-v0.1": {
        "description": "Provisional, single-source corpus: lineara.xyz only, L0 only, "
        "held-out documents excluded. For A2 work until the reconciled corpus-v1.0 (A1.6-A1.12).",
        "inputs": {
            "lineara.xyz": {
                "path": "data/raw/lineara.xyz/9c81beba669a/LinearAInscriptions.js",
                "commit": "9c81beba669a4ffec3f5b29d4e7748d02c060eff",
                "sha256": "9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e",
            }
        },
    }
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dedupe(docs):
    """Source records sharing an ID: keep the single non-empty one; refuse anything else."""
    by_id = collections.defaultdict(list)
    for d in docs:
        by_id[d.id].append(d)
    out, resolved = [], {}
    for doc_id, group in by_id.items():
        if len(group) == 1:
            out.append(group[0])
            continue
        non_empty = [d for d in group if d.lines]
        if len(non_empty) != 1:
            raise SystemExit(f"duplicate ID {doc_id} with {len(non_empty)} non-empty records; resolve by hand")
        out.append(non_empty[0])
        resolved[doc_id] = f"{len(group)} records; kept the only non-empty one"
    return out, resolved


def build(version: str, out_root: Path = REPO / "data/processed") -> dict:
    spec = RELEASES[version]
    src = spec["inputs"]["lineara.xyz"]
    path = REPO / src["path"]
    if not path.exists():
        raise SystemExit(f"missing input {path}; run data/raw/lineara.xyz/fetch.py")
    got = sha256(path)
    if got != src["sha256"]:
        raise SystemExit(f"HASH MISMATCH for {path}: {got}")
    held = load_heldout().get("lineara.xyz", set())
    docs, duplicates = dedupe(lineara.load_documents(path, held))
    docs.sort(key=lambda d: d.id)

    out_dir = out_root / version
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "documents.jsonl"
    out.write_text("".join(d.to_json() + "\n" for d in docs), encoding="utf-8")

    types = collections.Counter(t.type for d in docs for ln in d.lines for t in ln)
    manifest = {
        "version": version,
        "description": spec["description"],
        "layer": "L0",
        "inputs": spec["inputs"],
        "heldout_excluded": sorted(held),
        "duplicate_ids_resolved": duplicates,
        "documents": len(docs),
        "lines": sum(len(d.lines) for d in docs),
        "token_types": dict(sorted(types.items())),
        "documents_jsonl_sha256": sha256(out),
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="corpus-v0.1", choices=sorted(RELEASES))
    args = ap.parse_args()
    m = build(args.version)
    print(json.dumps({k: m[k] for k in ("version", "documents", "lines", "token_types", "documents_jsonl_sha256")}, indent=2))


if __name__ == "__main__":
    main()
