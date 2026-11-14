"""data/raw/younger/fetch.py: copying from a folder never accepts a file with the wrong hash."""
import hashlib
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "younger_fetch", Path(__file__).resolve().parents[1] / "data/raw/younger/fetch.py")
yf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yf)


def setup(tmp_path, monkeypatch, contents):
    here = tmp_path / "younger"
    here.mkdir()
    lines = [f"{hashlib.sha256(b'good ' + name.encode()).hexdigest()}  snap/{name}" for name in contents]
    (here / "SHA256SUMS").write_text("# comment\n" + "\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setattr(yf, "HERE", here)
    monkeypatch.setattr(yf, "SUMS", here / "SHA256SUMS")
    src = tmp_path / "src"
    src.mkdir()
    for name, data in contents.items():
        if data is not None:
            (src / name).write_bytes(data)
    return here, src


def test_copies_and_verifies_matching_files(tmp_path, monkeypatch):
    here, src = setup(tmp_path, monkeypatch, {"a.pdf": b"good a.pdf", "b.pdf": b"good b.pdf"})
    assert yf.main(["--from", str(src)]) == 0
    assert (here / "snap/a.pdf").read_bytes() == b"good a.pdf" and (here / "snap/b.pdf").exists()
    assert yf.main([]) == 0  # verify only


def test_wrong_version_is_not_copied_and_fails(tmp_path, monkeypatch):
    here, src = setup(tmp_path, monkeypatch, {"a.pdf": b"good a.pdf", "b.pdf": b"re-uploaded version"})
    assert yf.main(["--from", str(src)]) == 1
    assert (here / "snap/a.pdf").exists() and not (here / "snap/b.pdf").exists()


def test_missing_file_fails(tmp_path, monkeypatch):
    here, src = setup(tmp_path, monkeypatch, {"a.pdf": b"good a.pdf", "b.pdf": None})
    assert yf.main(["--from", str(src)]) == 1
    assert yf.main(["--from", str(tmp_path / "nowhere")]) == 1
