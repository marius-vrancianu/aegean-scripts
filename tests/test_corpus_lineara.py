import json
from pathlib import Path

import pytest

from aegean.corpus.lineara import LACUNA, tokenize

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "data/processed/corpus-v0.1/documents.jsonl"
MANIFEST = REPO / "data/processed/corpus-v0.1/MANIFEST.json"

KU, RO = "\U00010642", "\U00010601"  # LINEAR A SIGN AB081, AB002
FORTY, FIVE = "\U00010113", "\U0001010b"
J = "\U00010746"  # LINEAR A SIGN A707 J


def test_tokenize_group_numeral_fraction():
    assert tokenize(KU + RO).signs == ["AB081", "AB002"]
    n = tokenize(FORTY + FIVE)
    assert (n.type, n.value) == ("numeral", 45)
    f = tokenize(J)
    assert (f.type, f.fractions) == ("fraction", ["J"])


def test_tokenize_damage_markers():
    t = tokenize(FIVE + LACUNA)
    assert t.type == "numeral" and t.damaged_right and not t.damaged_left
    assert tokenize(LACUNA).type == "lacuna"


needs_corpus = pytest.mark.skipif(not CORPUS.exists(), reason="run `python -m aegean.corpus.build` first")


@needs_corpus
def test_corpus_matches_manifest_and_excludes_heldout():
    import hashlib

    m = json.loads(MANIFEST.read_text())
    assert hashlib.sha256(CORPUS.read_bytes()).hexdigest() == m["documents_jsonl_sha256"]
    ids = {json.loads(l)["id"] for l in CORPUS.open(encoding="utf-8")}
    assert len(ids) == m["documents"]
    assert not ids & set(m["heldout_excluded"])
