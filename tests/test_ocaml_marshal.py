"""Hand-built fixtures for the OCaml Marshal reader.

Expected byte sequences follow OCaml's runtime/extern.c encoding rules; each
fixture states the OCaml value it represents.
"""
import struct

import pytest

from aegean.corpus import ocaml_marshal as om
from aegean.corpus.sigla import extract_variables


def marshal(data: bytes, num_objects: int) -> bytes:
    return struct.pack(">IIIII", om.MAGIC_SMALL, len(data), num_objects, 0, 0) + data


def test_int_list():
    # [1; 2] = cons(1, cons(2, []))
    v = om.loads(marshal(bytes([0xA0, 0x41, 0xA0, 0x42, 0x40]), 2))
    assert om.to_list(v) == [1, 2]


def test_string_and_sharing():
    # let s = "ab" in (s, s): the second occurrence is a back-reference
    v = om.loads(marshal(bytes([0xA0, 0x22]) + b"ab" + bytes([0x04, 0x01]), 2))
    assert v.fields[0] == b"ab" and v.fields[1] is v.fields[0]


def test_option_and_atoms():
    # (Some "x", None, A) where A is a constant constructor -> immediate 0
    v = om.loads(marshal(bytes([0xB0, 0x90, 0x21]) + b"x" + bytes([0x40, 0x40]), 3))
    assert om.option(v.fields[0]) == b"x"
    assert om.option(v.fields[1]) is None


def test_large_int_and_block32():
    # (1000, -5) with a BLOCK32 header: size 2, tag 0 -> hd = 2 << 10
    data = bytes([om.CODE_BLOCK32]) + struct.pack(">I", 2 << 10)
    data += bytes([om.CODE_INT16]) + struct.pack(">h", 1000) + bytes([om.CODE_INT8]) + struct.pack(">b", -5)
    v = om.loads(marshal(data, 1))
    assert v.fields == [1000, -5]


def test_long_list_is_not_recursive():
    n = 5000
    data = bytes([0xA0, 0x41]) * n + bytes([0x40])
    assert om.to_list(om.loads(marshal(data, n))) == [1] * n


def test_header_counts_are_checked():
    with pytest.raises(om.MarshalError, match="object count"):
        om.loads(marshal(bytes([0xA0, 0x41, 0x40]), 7))


def test_bad_magic():
    with pytest.raises(om.MarshalError, match="magic"):
        om.loads(b"\x00" * 24)


def test_ocaml_literal_unescape():
    assert om.unescape_ocaml_literal(r"\132\149a\n\\\"") == bytes([132, 149]) + b'a\n\\"'


def test_database_js_layers():
    # `var x = '"\\065\\066"';` -> JS value "\065\066" -> OCaml bytes "AB"
    text = "/* X */\nvar x = '\"\\\\065\\\\066\"';\n"
    assert extract_variables(text) == {"x": b"AB"}
