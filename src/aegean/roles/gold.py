"""Labelled-picture gold set (A8.1; plan A8). Layer: L0 (L1 values are labels only).

  python -m aegean.roles.gold
  python -m aegean.roles.gold --witnesses PATH --allow-partial   # a build without all sources

Writes, under data/processed/gold/:
  gold-set.tsv            the answer key for A8.2, A8.3 and A8.8
  vessel-candidates.tsv   every vessel logogram in the training split and why it is or is not gold
  MANIFEST.json           hashes, parameters, status
and docs/reports/A8.1-gold-set.md. All four are generated; do not edit them.

Two kinds of gold item
----------------------
1. **Labelled pictures**, found in the witnesses. A vessel logogram is a
   drawing of a vessel (GORILA signs A400-A418; Unicode names each of them
   "VAS"). Where a sign-group is written over such a drawing, the group
   refers to that vessel, whatever the language. Two independent encodings
   show this:
   - SigLA gives each sign's bounding box. A sign-group counts as written
     over a vessel logogram if (a) it has two or more signs, (b) its
     horizontal extent overlaps the logogram's by at least MIN_OVERLAP of
     the narrower of the two, (c) its boxes reach into the logogram's box
     from above (vertical gap < 0) and its vertical centre is above the
     logogram's, and (d) its signs are small: mean height below
     MAX_SIZE_RATIO of the document's median sign height in sign-groups.
   - lineara.xyz has no layout. It encodes such a group as one item that
     starts with the vessel logogram and continues with two or more signs.
   Grade A: both sources show it. Grade B: one source shows it and the
   other does not have the document. Anything else stays in
   vessel-candidates.tsv with the reason, and is not gold.
   The thresholds were chosen after looking at the training data (the task
   is curation, not a test); they are recorded in the manifest.
2. **Literature items**, from data/gold-input/literature-items.tsv:
   KU-RO, KI-RO, names shared with Linear B. Their meaning is taken from
   publications. This module only finds where they occur in the training
   split, by exact match of L0 sign IDs.

Only the training split is read (aegean.corpus.load). A labelled picture
on a held-out document is not in this set.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import statistics
import sys
from pathlib import Path

from aegean.corpus import layers, load
from aegean.corpus.schema import base_id

REPO = Path(__file__).resolve().parents[3]
INPUT = REPO / "data/gold-input/literature-items.tsv"
OUT = REPO / "data/processed/gold"
REPORT = REPO / "docs/reports/A8.1-gold-set.md"
SOURCES = ("lineara.xyz", "sigla", "younger")
GROUP_KINDS = ("word", "logogram", "transaction", "unknown", "mixed")
MIN_OVERLAP = 0.5
MAX_SIZE_RATIO = 0.9
SCORING_GRADES = ("A", "B")
COLUMNS = ["id", "kind", "item_l1", "signs_l0", "role", "referent", "grade", "basis", "sources", "source_check",
           *[f"train_docs_{s}" for s in SOURCES], "n_train_docs", "note"]
CAND_COLUMNS = ["document", "source", "logogram", "components", "group_l1", "group_l0", "overlap", "gap",
                "size_ratio", "verdict", "reason"]
DUHOUX = ("Duhoux, Y. 2000-2001. Un inventaire linéaire A de vases: la tablette HT 31. Minos 35-36, 31-62 "
          "(https://revistas.usal.es/dos/index.php/0544-3733/article/download/16424/17038/56788)")
LICENCE = ("Derived in part from SigLA (© Ester Salgarella & Simon Castellan, https://sigla.phis.me, CC BY-NC-SA 4.0); "
           "the same terms apply. Other inputs: lineara.xyz and Younger 2024 (no licence stated). Holds document "
           "identifiers and short sign sequences, not full texts.")


def is_vessel(sign_id: str | None) -> bool:
    m = re.match(r"^A(4\d\d)", sign_id or "")
    return bool(m) and 400 <= int(m.group(1)) <= 418


def _is_fraction(sign_id: str | None) -> bool:
    return bool(sign_id) and sign_id[:2] == "A7" and sign_id[1:4].isdigit()


def label(sign_id: str | None) -> str:
    return "?" if not sign_id else (layers.l1_of(sign_id) or "*" + re.sub(r"^A(B)?0*", "", sign_id))


def l1(ids) -> str:
    return "-".join(label(i) for i in ids)


def _ids(tokens: list[dict]) -> list[str | None]:
    return [t.get("sign_id") for t in tokens if not _is_fraction(t.get("sign_id"))]


def _box(tokens: list[dict]) -> tuple[float, float, float, float]:
    """(x0, y0, x1, y1) around the tokens' bounding boxes (SigLA boxes are x, y, width, height)."""
    return (min(t["bbox"][0] for t in tokens), min(t["bbox"][1] for t in tokens),
            max(t["bbox"][0] + t["bbox"][2] for t in tokens), max(t["bbox"][1] + t["bbox"][3] for t in tokens))


# --- labelled pictures ----------------------------------------------------------------------

def sigla_candidates(w: dict) -> list[dict]:
    """One row per (vessel logogram, sign-group above it) in a SigLA witness; a logogram with none gets one row."""
    items = [it for ln in w["lines"] for it in ln["items"]]
    heights = [t["bbox"][3] for it in items if it["kind"] in GROUP_KINDS and len(it["tokens"]) >= 2
               for t in it["tokens"] if t.get("bbox")]
    median = statistics.median(heights) if heights else None
    out = []
    for it in items:
        for t in it["tokens"]:
            if not (is_vessel(t.get("sign_id")) or any(is_vessel(c) for c in t.get("components", []))):
                continue
            row = {"document": w["doc_key"], "source": "sigla", "logogram": base_id(t["sign_id"]),
                   "components": "+".join(t.get("components", []))}
            found = []
            if t.get("bbox") and not t.get("components"):
                lx, ly, lw, lh = t["bbox"]
                for g in items:
                    toks = g["tokens"]
                    if g["kind"] not in GROUP_KINDS or len(toks) < 2 or not all(x.get("bbox") for x in toks):
                        continue
                    x0, y0, x1, y1 = _box(toks)
                    overlap = max(0.0, min(x1, lx + lw) - max(x0, lx)) / max(1.0, min(x1 - x0, lw))
                    gap = (ly - y1) / max(lh, 1)
                    if overlap < MIN_OVERLAP or gap >= 0 or (y0 + y1) / 2 >= ly + lh / 2:
                        continue
                    size = statistics.mean(x["bbox"][3] for x in toks) / median if median else float("nan")
                    small = size < MAX_SIZE_RATIO
                    found.append({**row, "group_l0": " ".join(i or "?" for i in _ids(toks)), "group_l1": l1(_ids(toks)),
                                  "overlap": f"{overlap:.2f}", "gap": f"{gap:.2f}", "size_ratio": f"{size:.2f}",
                                  "verdict": "label" if small else "not_gold",
                                  "reason": "small signs written over the logogram" if small else
                                  f"over the logogram, but signs are of normal size (ratio >= {MAX_SIZE_RATIO}): "
                                  "ordinary line layout cannot be excluded"})
            if not found:
                reason = ("ligature of a vessel sign with other signs: an adjunct, not a sign-group"
                          if t.get("components") else "no sign-group written over it")
                found = [{**row, "verdict": "not_gold", "reason": reason}]
            out += found
    return out


def lineara_candidates(w: dict) -> list[dict]:
    """One row per item that contains a vessel logogram in a lineara.xyz witness."""
    out = []
    for ln in w["lines"]:
        for it in ln["items"]:
            ids = _ids(it["tokens"])
            if it["kind"] not in GROUP_KINDS or not any(is_vessel(i) for i in ids):
                continue
            row = {"document": w["doc_key"], "source": "lineara.xyz", "logogram": base_id(next(i for i in ids if is_vessel(i)))}
            if is_vessel(ids[0]) and len(ids) >= 3 and not any(is_vessel(i) for i in ids[1:]):
                out.append({**row, "group_l0": " ".join(i or "?" for i in ids[1:]), "group_l1": l1(ids[1:]),
                            "verdict": "label", "reason": "logogram and sign-group encoded as one item"})
            else:
                out.append({**row, "verdict": "not_gold", "reason": "vessel logogram stands alone in its item"})
    return out


def labelled_pictures(ws: list[dict]) -> tuple[list[dict], list[dict]]:
    """(gold rows, all candidate rows)."""
    cands = []
    have = collections.defaultdict(set)
    for w in ws:
        have[w["doc_key"]].add(w["source"])
        if w["source"] == "sigla":
            cands += sigla_candidates(w)
        elif w["source"] == "lineara.xyz":
            cands += lineara_candidates(w)
    seen = collections.defaultdict(set)  # (document, logogram, group) -> sources that show a label
    for c in cands:
        if c["verdict"] == "label":
            seen[(c["document"], c["logogram"], c["group_l0"])].add(c["source"])
    gold = []
    for (doc, logo, group), srcs in sorted(seen.items()):
        others = (have[doc] & {"sigla", "lineara.xyz"}) - srcs
        if others:  # the other layout-bearing source has the document and does not show the label
            for c in cands:
                if (c["document"], c["logogram"], c.get("group_l0")) == (doc, logo, group):
                    c["verdict"], c["reason"] = "not_gold", c["reason"] + f"; not shown by {', '.join(sorted(others))}"
            continue
        ids = group.split(" ")
        gold.append({
            "kind": "labelled_picture", "item_l1": l1(ids), "signs_l0": group, "role": "vessel_designation",
            "referent": f"the vessel drawn as sign {logo}", "grade": "A" if len(srcs) == 2 else "B",
            "basis": "sign-group written over a vessel logogram (" + "; ".join(sorted(srcs)) + ")",
            "sources": f"witnesses; {DUHOUX}" if doc == "HT 31" else "witnesses",
            "source_check": "witnesses read; publication seen as search excerpt only" if doc == "HT 31" else "witnesses read",
            **{f"train_docs_{s}": doc if s in srcs else "" for s in SOURCES}, "n_train_docs": 1,
            "note": "The object is known; the word's exact sense (vessel type, content, material, owner) is not.",
        })
    cands.sort(key=lambda c: (c["document"], c["source"], c["logogram"], c.get("group_l0", "")))
    return gold, cands


# --- literature items ------------------------------------------------------------------------

def value_table() -> dict[str, str]:
    """{conventional value: L0 base sign ID}, from the uniform L1 table (docs/layers.md)."""
    return {v: base_id(k) for k, v in layers.LB_VALUES.items()}


def literature_items(ws: list[dict], path: Path = INPUT) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    table = value_table()
    groups = collections.defaultdict(lambda: collections.defaultdict(set))  # sign tuple -> source -> documents
    inside = collections.defaultdict(set)
    wanted = {tuple(table[v] for v in r["item_l1"].split("-")) for r in rows}
    for w in ws:
        for ln in w["lines"]:
            for it in ln["items"]:
                if it["kind"] not in GROUP_KINDS:
                    continue
                ids = tuple(base_id(i) if i else None for i in _ids(it["tokens"]))
                groups[ids][w["source"]].add(w["doc_key"])
                for seq in wanted:
                    if len(ids) > len(seq) and any(ids[i:i + len(seq)] == seq for i in range(len(ids) - len(seq) + 1)):
                        inside[seq].add(w["doc_key"])
    out = []
    for r in rows:
        seq = tuple(table[v] for v in r["item_l1"].split("-"))
        docs = groups.get(seq, {})
        all_docs = sorted(set().union(*docs.values())) if docs else []
        note = r["note"]
        if inside[seq]:
            note = (note + " " if note else "") + f"Also inside longer sign-groups on {len(inside[seq])} training document(s)."
        if not all_docs:
            note = (note + " " if note else "") + "Not attested as a sign-group of its own in the training split."
        out.append({"kind": "literature", "item_l1": r["item_l1"], "signs_l0": " ".join(seq), "role": r["role"],
                    "referent": r["referent"], "grade": r["grade"],
                    "basis": f"literature (survey confidence: {r['survey_confidence']})",
                    "sources": r["sources"], "source_check": r["source_check"],
                    **{f"train_docs_{s}": ";".join(sorted(docs.get(s, ()))) for s in SOURCES},
                    "n_train_docs": len(all_docs), "note": note})
    return out


# --- build -----------------------------------------------------------------------------------

def _tsv(rows: list[dict], columns: list[str]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, columns, delimiter="\t", lineterminator="\n", extrasaction="ignore", restval="")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def build(witnesses_path: Path = load.WITNESSES, allow_partial: bool = False) -> tuple[list[dict], list[dict], dict]:
    ws = load.witnesses(path=witnesses_path, verify_hash=not allow_partial)
    present = [s for s in SOURCES if any(w["source"] == s for w in ws)]
    missing = [s for s in SOURCES if s not in present]
    if missing and not allow_partial:
        raise SystemExit(f"sources missing from {witnesses_path}: {missing}")
    pictures, cands = labelled_pictures(ws)
    gold = pictures + literature_items(ws)
    for n, g in enumerate(gold, 1):
        g["id"] = f"G{n:03d}"
    release = json.loads(load.RELEASE_MANIFEST.read_text(encoding="utf-8"))["components"]["witnesses"]["sha256"]
    wsha = hashlib.sha256(witnesses_path.read_bytes()).hexdigest()
    partial = bool(missing) or wsha != release
    gold_tsv = _tsv(gold, COLUMNS)
    manifest = {
        "task": "A8.1", "layer": "L0", "split": "train",
        "status": "DRAFT, not frozen: " + ("; ".join(filter(None, [
            f"partial build (missing: {', '.join(missing) or 'none'}; witnesses file is not the release file)" if partial else "",
            "literature sources not yet checked against the publications"]))),
        "partial_build": partial, "sources_present": present, "sources_missing": missing,
        "witnesses_sha256": wsha, "literature_input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "parameters": {"vessel_signs": "A400-A418", "min_overlap": MIN_OVERLAP, "max_size_ratio": MAX_SIZE_RATIO,
                       "scoring_grades": list(SCORING_GRADES)},
        "counts": {"items": len(gold), "by_kind": dict(collections.Counter(g["kind"] for g in gold)),
                   "by_grade": dict(sorted(collections.Counter(g["grade"] for g in gold).items())),
                   "by_role_scoring_grades": dict(sorted(collections.Counter(
                       g["role"] for g in gold if g["grade"] in SCORING_GRADES and g["n_train_docs"]).items())),
                   "scorable": sum(g["grade"] in SCORING_GRADES and g["n_train_docs"] > 0 for g in gold),
                   "vessel_candidate_rows": len(cands)},
        "gold_set_sha256": hashlib.sha256(gold_tsv.encode("utf-8")).hexdigest(),
        "licence": LICENCE,
    }
    return gold, cands, manifest


def render(gold: list[dict], cands: list[dict], m: dict) -> str:
    c = m["counts"]
    L = ["# A8.1 — Labelled-picture gold set", "",
         "Generated by `python -m aegean.roles.gold`. Do not edit. Files: `data/processed/gold/`.", "",
         f"**Status: {m['status']}.**", "",
         "**What this is.** The answer key for A8.2, A8.3 and A8.8: sign-groups whose function is known without "
         "reading the language. It is data, not a finding, and tests nothing. Layer L0; the transliterations are "
         "conventional Linear B values (L1), used as labels. Training split only.", "",
         f"**Size.** {c['items']} items; {c['scorable']} are usable for scoring (grade A or B and attested in the "
         "training split): " + ", ".join(f"{v} {k}" for k, v in c["by_role_scoring_grades"].items()) + ". "
         "Plan A8 expected 20 to 40 items; **the usable key is at the bottom of that range or below it**, and "
         "accuracy measured against it will carry a wide interval.", "",
         "## Labelled pictures", "",
         "A vessel logogram is a drawing of a vessel. A sign-group written over the drawing refers to that vessel "
         "whatever the language. The criteria are in the module docstring; they were set after looking at the "
         "training data.", "",
         "| ID | Document | Sign-group | L0 signs | Vessel sign | Grade | Evidence |", "|---|---|---|---|---|---|---|"]
    for g in gold:
        if g["kind"] == "labelled_picture":
            doc = next(g[f"train_docs_{s}"] for s in SOURCES if g[f"train_docs_{s}"])
            L.append(f"| {g['id']} | {doc} | {g['item_l1']} | {g['signs_l0']} | {g['referent'].split()[-1]} | "
                     f"{g['grade']} | {g['basis'].split('(')[-1].rstrip(')')} |")
    pics = [g for g in gold if g["kind"] == "labelled_picture"]
    docs = sorted({g[f"train_docs_{s}"] for g in pics for s in SOURCES if g[f"train_docs_{s}"]})
    L += ["", f"**All {len(pics)} come from {len(docs)} document(s): {', '.join(docs)}.** "
          "What is known is the object (a vessel). What the word says about it (its type, its contents, its "
          "material, an owner) is not known, so the role is `vessel_designation`, not a translation.", ""]
    if "HT 31" in docs:
        L += ["The reading agrees with the published edition as far as a search excerpt shows it (Duhoux 2000-2001, "
              "*Minos* 35-36, 31-62: vessel signs with qa-\\*56, su-pu, ka-ro-\\*56 and su-\\*56-ra written above "
              "them). Confidence that the five items are labels of vessels: high. The article itself was not read. "
              "`*56` is a sign with no agreed sound value; some editions write it PA3.", ""]
    rejected = [x for x in cands if x["verdict"] != "label" and x.get("group_l1")]
    if rejected:
        L += ["**Looked like labels, not accepted** (in `vessel-candidates.tsv` with measurements):", ""]
        L += [f"- {x['document']} ({x['source']}): {x['group_l1']} at vessel sign {x['logogram']}: {x['reason']}."
              for x in rejected]
        L.append("")
    adj = collections.Counter((x["logogram"], x["components"]) for x in cands if x.get("components"))
    if adj:
        L += ["**Composite vessel signs (ligatures), as SigLA decomposes them.** Not gold: an attached sign is not a "
              "sign-group, and what it stands for is unknown. Those with a syllabic sign are the natural input for "
              "the abbreviation test (A8.3); those with a fraction sign (E, F, Ω) are a different matter.", "",
              "| Composite sign | Components | Occurrences (training, SigLA) |", "|---|---|---|"]
        L += [f"| {k[0]} | {' + '.join(label(p) if not is_vessel(p) else p for p in k[1].split('+'))} | {v} |"
              for k, v in sorted(adj.items())]
        L.append("")
    L += ["## Literature items", "",
          "Meaning taken from publications; this module only locates them in the training split. "
          "**No primary source was read for this table** (see \"Source check\"). Grades are Claude's proposal "
          "(`data/gold-input/README.md`).", "",
          "| ID | Sign-group | Role | Referent | Grade | Training documents (any source) | Source check |",
          "|---|---|---|---|---|---|---|"]
    for g in gold:
        if g["kind"] == "literature":
            L.append(f"| {g['id']} | {g['item_l1']} | {g['role']} | {g['referent']} | {g['grade']} | "
                     f"{g['n_train_docs']} | {g['source_check']} |")
    L += ["", "Notes per item, sources and the documents per source are in `gold-set.tsv`.", "",
          "## Limits", "",
          "- **Circularity for A8.8.** KU-RO, KI-RO and the names were identified by scholars from the same "
          "contextual cues a role classifier uses (position, numbers, Linear B parallels). Scoring a classifier on "
          "them measures agreement with that scholarship, not independent truth. Only the labelled pictures are "
          "free of this, and they are five items on one tablet by one scribe.",
          "- **Names versus places** rest on Linear B, where the two are told apart partly by Greek word forms.",
          "- **Training split only.** Occurrences on the 90 held-out documents are not listed and were not looked "
          "at. A published attestation that is missing here (for example HT 97 for PA-I-TO) is on a document "
          "outside the training split.",
          "- **Layout evidence comes from SigLA alone**; lineara.xyz contributes only its item boundaries. A label "
          "on a document that SigLA does not have can at best reach grade B.",
          "- **Grade C items are not for scoring.** They are listed so that nobody adds them later unnoticed.", "",
          "## Before freezing", ""]
    steps = (["Rebuild on the full witnesses file (adds Younger's readings)."] if m["partial_build"] else []) + [
        "Check every literature row against its publication, and identify the *Minos* article "
        "(author and title were not shown in the excerpt).",
        "Marius confirms or changes the grades.",
        "Then record `gold_set_sha256` from the manifest in the first A8 hypothesis file."]
    L += [f"{n}. {t}" for n, t in enumerate(steps, 1)] + [""]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--witnesses", type=Path, default=load.WITNESSES)
    ap.add_argument("--allow-partial", action="store_true")
    args = ap.parse_args(argv)
    gold, cands, m = build(args.witnesses, args.allow_partial)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gold-set.tsv").write_text(_tsv(gold, COLUMNS), encoding="utf-8")
    (OUT / "vessel-candidates.tsv").write_text(_tsv(cands, CAND_COLUMNS), encoding="utf-8")
    (OUT / "MANIFEST.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# Gold set (A8.1)\n\nGenerated by `python -m aegean.roles.gold`; never edit by "
                                   f"hand. Report: `docs/reports/A8.1-gold-set.md`.\n\n**Licence: CC BY-NC-SA 4.0.** "
                                   f"{LICENCE}\n", encoding="utf-8")
    REPORT.write_text(render(gold, cands, m), encoding="utf-8")
    print(json.dumps(m["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
