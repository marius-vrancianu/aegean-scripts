"""The corpus loader every analysis uses from corpus-v1.0 on (A1.12).

    from aegean.corpus import load
    docs = load.documents()        # training split of the default analysis set
    ws = load.witnesses()          # their witnesses, one dict per source reading (docs/schema.md)

By default the frozen held-out split (data/heldout.txt, `split:` lines) is
withheld. Reading it needs the ID of a frozen confirmatory hypothesis:

    ws = load.witnesses(split="heldout", heldout_for="H-A3-01")

`heldout_for` is accepted only if `hypotheses/<ID>.md`
  1. exists,
  2. is byte-identical to the file on `origin/main` (merged = pre-registered
     and immutable, CLAUDE.md rule 3), and
  3. declares itself confirmatory with a line `- **Type:** confirmatory`
     (CLAUDE.md rule 10).
Anything else raises HeldoutAccessError. The check stops mistakes, not a
determined caller: the split documents are in the corpus files, and reading
those files directly bypasses this module. Do not do that.

  python -m aegean.corpus.load                                  # counts, training split
  python -m aegean.corpus.load --split heldout --heldout-for H-A3-01
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from aegean.corpus.heldout import HELDOUT_FILE, load_split

REPO = Path(__file__).resolve().parents[3]
DOCUMENT_LIST = REPO / "data/processed/document-list/document-list.tsv"
WITNESSES = REPO / "data/processed/corpus-v1.0-pre/witnesses.jsonl"
RELEASE_MANIFEST = REPO / "data/processed/corpus-v1.0/MANIFEST.json"

SPLITS = ("train", "heldout", "all")
HYPOTHESIS_ID_RE = re.compile(r"H-A\d+-\d+")
CONFIRMATORY_RE = re.compile(r"^\s*[-*]?\s*\*\*Type:\*\*\s*confirmatory\b", re.IGNORECASE | re.MULTILINE)
MAIN_REFS = ("origin/main", "main")


class HeldoutAccessError(RuntimeError):
    """The held-out split was requested without a frozen confirmatory hypothesis."""


def _on_main(repo: Path, rel: str) -> bytes | None:
    """The file's content on main, or None if no main ref has it. Raises if this is not a git checkout."""
    found_ref = False
    for ref in MAIN_REFS:
        try:
            r = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{rel}"], capture_output=True)
        except FileNotFoundError as e:  # no git executable
            raise HeldoutAccessError("git is needed to verify that the hypothesis is merged") from e
        if r.returncode == 0:
            return r.stdout
        if subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", ref],
                          capture_output=True).returncode == 0:
            found_ref = True
    if not found_ref:
        raise HeldoutAccessError(f"no {' or '.join(MAIN_REFS)} ref in {repo}: cannot verify that the hypothesis is merged")
    return None


def check_frozen_hypothesis(hypothesis_id: str, repo: Path = REPO) -> Path:
    """Return the hypothesis file if it is merged, unmodified and confirmatory; raise HeldoutAccessError otherwise."""
    if not isinstance(hypothesis_id, str) or not HYPOTHESIS_ID_RE.fullmatch(hypothesis_id):
        raise HeldoutAccessError(f"not a hypothesis ID (H-A<n>-<nn>): {hypothesis_id!r}")
    rel = f"hypotheses/{hypothesis_id}.md"
    path = repo / rel
    if not path.is_file():
        raise HeldoutAccessError(f"{rel} does not exist: register and merge the hypothesis first (CLAUDE.md rule 3)")
    merged = _on_main(repo, rel)
    if merged is None:
        raise HeldoutAccessError(f"{rel} is not on main: a hypothesis is frozen only once it is merged")
    if merged != path.read_bytes():
        raise HeldoutAccessError(f"{rel} differs from the merged version on main")
    if not CONFIRMATORY_RE.search(merged.decode("utf-8", errors="replace")):
        raise HeldoutAccessError(f"{rel} does not declare '- **Type:** confirmatory' (CLAUDE.md rule 10): "
                                 "exploratory hypotheses use the training split")
    return path


def _authorise(split: str, heldout_for: str | None, repo: Path) -> None:
    if split not in SPLITS:
        raise ValueError(f"split must be one of {SPLITS}, got {split!r}")
    if split == "train":
        if heldout_for is not None:
            raise ValueError("heldout_for is given but split is 'train'; ask for split='heldout' or 'all'")
        return
    if heldout_for is None:
        raise HeldoutAccessError(f"split={split!r} needs heldout_for=<frozen confirmatory hypothesis ID>")
    check_frozen_hypothesis(heldout_for, repo)
    print(f"HELD-OUT ACCESS: split={split!r} released for {heldout_for}. A confirmatory test runs once; "
          "record the outcome in hypotheses/outcomes/.", file=sys.stderr)


def documents(*, split: str = "train", heldout_for: str | None = None, analysis_default: bool = True,
              document_list: Path = DOCUMENT_LIST, heldout_file: Path = HELDOUT_FILE,
              repo: Path = REPO) -> list[dict]:
    """Rows of the canonical document list, each with a `split` field ("train" or "heldout").

    analysis_default=True keeps the default analysis set (docs/inclusion-rules.md). With False, documents
    outside that set are returned too; they were never part of the draw and count as "train".
    """
    _authorise(split, heldout_for, repo)
    held = load_split(heldout_file)
    with document_list.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    missing = held - {r["key"] for r in rows}
    if missing:
        raise RuntimeError(f"{len(missing)} held-out keys are not in the document list (e.g. {sorted(missing)[:3]}): "
                           "the list changed after the freeze")
    out = []
    for r in rows:
        r["split"] = "heldout" if r["key"] in held else "train"
        if analysis_default and r["analysis_default"] != "true":
            continue
        if split == "all" or r["split"] == split:
            out.append(r)
    return out


def _source_index(rows: list[dict]) -> dict[str, str]:
    """{"<source>:<source_id>": document key} from the list's source_ids column."""
    return {sid: r["key"] for r in rows for sid in r["source_ids"].split(";") if sid}


def witnesses(*, split: str = "train", heldout_for: str | None = None, analysis_default: bool = True,
              path: Path = WITNESSES, verify_hash: bool = True, document_list: Path = DOCUMENT_LIST,
              heldout_file: Path = HELDOUT_FILE, repo: Path = REPO) -> list[dict]:
    """Witness records (docs/schema.md) of the selected documents, each with a `doc_key` field added.

    A witness that cannot be matched to a listed document is an error, not training data. verify_hash checks the file against the
    release manifest (a mismatch is a hard error, CLAUDE.md).
    """
    _authorise(split, heldout_for, repo)
    if not path.exists():
        raise FileNotFoundError(f"{path} is not built; run python -m aegean.corpus.build_layers")
    if verify_hash:
        want = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))["components"]["witnesses"]["sha256"]
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            raise RuntimeError(f"HASH MISMATCH for {path}: {got}, release manifest has {want}")
    held = load_split(heldout_file)
    with document_list.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    index = _source_index(rows)
    wanted = {r["key"] for r in rows if not analysis_default or r["analysis_default"] == "true"}
    out = []
    with path.open(encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            w = json.loads(line)
            sid = f"{w['source']}:{w['source_id']}"
            key = index.get(sid)
            if key is None:
                raise RuntimeError(f"{path}:{n}: witness {sid} is not in the document list")
            is_held = key in held
            if key not in wanted or (split == "train" and is_held) or (split == "heldout" and not is_held):
                continue
            w["doc_key"] = key
            out.append(w)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", choices=SPLITS, default="train")
    ap.add_argument("--heldout-for", metavar="H-A<n>-<nn>", help="frozen confirmatory hypothesis that releases the held-out split")
    ap.add_argument("--all-listed", action="store_true", help="include documents outside the default analysis set")
    args = ap.parse_args(argv)
    try:
        docs = documents(split=args.split, heldout_for=args.heldout_for, analysis_default=not args.all_listed)
    except HeldoutAccessError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    print(json.dumps({"split": args.split, "documents": len(docs)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
