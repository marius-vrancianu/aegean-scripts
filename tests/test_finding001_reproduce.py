import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "reproduce", Path(__file__).resolve().parents[1] / "experiments" / "finding-001" / "reproduce.py"
)
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)


def test_strip_records_removes_only_named_records():
    js = 'var x = [\n["HT1",{"a":1}],\n["KX9",{"a":2}],\n["HT2",{"a":3}]];'
    out, n = rep.strip_records(js, {"KX9"})
    assert n == 1
    assert '["KX9",' not in out and '["HT1",' in out and '["HT2",' in out
