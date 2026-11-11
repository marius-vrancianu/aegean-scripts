"""The corpus loader's held-out gate (A1.12). Everything runs on a throwaway repository."""
import json
import subprocess

import pytest

from aegean.corpus import load

HEADER = "key\tsource_ids\tanalysis_default\n"
LIST = HEADER + ("AA 1\tsigla:AA 1;lineara.xyz:AA1a;lineara.xyz:AA1b\ttrue\n"
                 "AA 2\tsigla:AA 2\ttrue\n"
                 "AA 3\tsigla:AA 3\ttrue\n"
                 "BB Zb 1\tlineara.xyz:BBZb1\tfalse\n")
HYP = "# H-A3-01 — test\n\n- **Logged:** 2026-11-11\n- **Type:** {type}\n- **Status:** pre-registered\n"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                    "-c", "commit.gpgsign=false", *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "hypotheses").mkdir()
    (tmp_path / "list.tsv").write_text(LIST, encoding="utf-8")
    (tmp_path / "heldout.txt").write_text("# test\nlineara.xyz:XX1\nsplit:AA 2\n", encoding="utf-8")
    ws = [("sigla", "AA 1"), ("lineara.xyz", "AA1a"), ("lineara.xyz", "AA1b"), ("sigla", "AA 2"),
          ("sigla", "AA 3"), ("lineara.xyz", "BBZb1")]
    (tmp_path / "witnesses.jsonl").write_text(
        "".join(json.dumps({"source": s, "source_id": i, "lines": []}) + "\n" for s, i in ws), encoding="utf-8")
    (tmp_path / "hypotheses/H-A3-01.md").write_text(HYP.format(type="confirmatory"), encoding="utf-8")
    (tmp_path / "hypotheses/H-A3-02.md").write_text(HYP.format(type="exploratory"), encoding="utf-8")
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def kw(repo, **extra):
    return dict(document_list=repo / "list.tsv", heldout_file=repo / "heldout.txt", repo=repo, **extra)


def keys(rows, field="key"):
    return sorted({r[field] for r in rows})


def test_default_is_the_training_split_of_the_analysis_set(repo):
    assert keys(load.documents(**kw(repo))) == ["AA 1", "AA 3"]
    ws = load.witnesses(path=repo / "witnesses.jsonl", verify_hash=False, **kw(repo))
    assert keys(ws, "doc_key") == ["AA 1", "AA 3"] and len(ws) == 4  # both sides of AA 1


def test_documents_outside_the_analysis_set_are_training_when_asked_for(repo):
    assert keys(load.documents(analysis_default=False, **kw(repo))) == ["AA 1", "AA 3", "BB Zb 1"]


@pytest.mark.parametrize("split", ["heldout", "all"])
def test_heldout_needs_a_hypothesis(repo, split):
    with pytest.raises(load.HeldoutAccessError, match="needs heldout_for"):
        load.documents(split=split, **kw(repo))
    with pytest.raises(load.HeldoutAccessError):
        load.witnesses(split=split, path=repo / "witnesses.jsonl", verify_hash=False, **kw(repo))


def test_frozen_confirmatory_hypothesis_releases_the_split(repo, capsys):
    assert keys(load.documents(split="heldout", heldout_for="H-A3-01", **kw(repo))) == ["AA 2"]
    assert "HELD-OUT ACCESS" in capsys.readouterr().err
    assert keys(load.documents(split="all", heldout_for="H-A3-01", **kw(repo))) == ["AA 1", "AA 2", "AA 3"]
    ws = load.witnesses(split="heldout", heldout_for="H-A3-01", path=repo / "witnesses.jsonl", verify_hash=False, **kw(repo))
    assert keys(ws, "doc_key") == ["AA 2"]


@pytest.mark.parametrize("bad", ["H-A3-99", "H-A3-02", "../CLAUDE", "", "h-a3-01", None])
def test_other_ids_are_refused(repo, bad):
    # unregistered; exploratory; not an ID
    with pytest.raises(load.HeldoutAccessError):
        load.documents(split="heldout", heldout_for=bad, **kw(repo))


def test_unmerged_hypothesis_is_refused(repo):
    (repo / "hypotheses/H-A3-03.md").write_text(HYP.format(type="confirmatory"), encoding="utf-8")
    with pytest.raises(load.HeldoutAccessError, match="not on main"):
        load.documents(split="heldout", heldout_for="H-A3-03", **kw(repo))
    git(repo, "checkout", "-q", "-b", "work")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "on a branch only")
    with pytest.raises(load.HeldoutAccessError, match="not on main"):
        load.documents(split="heldout", heldout_for="H-A3-03", **kw(repo))


def test_edited_hypothesis_is_refused(repo):
    p = repo / "hypotheses/H-A3-02.md"
    p.write_text(p.read_text(encoding="utf-8").replace("exploratory", "confirmatory"), encoding="utf-8")
    with pytest.raises(load.HeldoutAccessError, match="differs from the merged version"):
        load.documents(split="heldout", heldout_for="H-A3-02", **kw(repo))


def test_without_git_history_nothing_is_released(repo, tmp_path_factory):
    bare = tmp_path_factory.mktemp("nogit")
    (bare / "hypotheses").mkdir()
    (bare / "hypotheses/H-A3-01.md").write_text(HYP.format(type="confirmatory"), encoding="utf-8")
    with pytest.raises(load.HeldoutAccessError, match="cannot verify"):
        load.check_frozen_hypothesis("H-A3-01", bare)


def test_heldout_for_with_training_split_is_a_usage_error(repo):
    with pytest.raises(ValueError):
        load.documents(heldout_for="H-A3-01", **kw(repo))


def test_unlisted_witness_is_an_error_not_training_data(repo):
    p = repo / "witnesses.jsonl"
    p.write_text(p.read_text(encoding="utf-8") + json.dumps({"source": "sigla", "source_id": "ZZ 9"}) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="not in the document list"):
        load.witnesses(path=p, verify_hash=False, **kw(repo))


def test_heldout_key_missing_from_the_list_is_an_error(repo):
    (repo / "heldout.txt").write_text("split:AA 99\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="not in the document list"):
        load.documents(**kw(repo))


def test_real_document_list_training_plus_heldout_is_the_analysis_set():
    from aegean.corpus.heldout import load_split
    train = load.documents()
    assert len(train) + len(load_split()) == 568
    assert not {r["key"] for r in train} & load_split()
