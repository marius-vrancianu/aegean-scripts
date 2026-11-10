"""Read OCaml `Marshal` data (the "intern" format) into Python values.

SigLA's `database.js` stores its corpus as OCaml-marshalled values inside
JavaScript string literals (DATA_SOURCES.md, A1.4). This module decodes the
generic value graph; it knows nothing about SigLA's record layout, which is
interpreted in `aegean.corpus.sigla`.

Format reference: OCaml runtime `runtime/intern.c` and `runtime/caml/intext.h`
(OCaml 4.x / 5.x, uncompressed). Mapping:

- immediate int          -> Python int
- string / bytes         -> Python bytes (decoding is the caller's choice)
- block (tag, fields)    -> Block(tag, fields); atoms (size 0) -> Block(tag, [])
- float                  -> Python float; float array -> FloatArray(list)
- custom int32/int64/nativeint -> Python int

Shared (back-referenced) objects decode to the same Python object, so cycles
are possible; `Block.__repr__` is cycle-safe. Decoding is iterative, because
OCaml lists are nested cons cells and a long list would overflow Python's
recursion limit.

The header's object count and data length are checked against what was read:
a mismatch is a hard error (a cheap, strong self-check on the decoder).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

MAGIC_SMALL = 0x8495A6BE
MAGIC_BIG = 0x8495A6BF
MAGIC_COMPRESSED = 0x8495A6BD

PREFIX_SMALL_BLOCK = 0x80
PREFIX_SMALL_INT = 0x40
PREFIX_SMALL_STRING = 0x20
CODE_INT8, CODE_INT16, CODE_INT32, CODE_INT64 = 0x00, 0x01, 0x02, 0x03
CODE_SHARED8, CODE_SHARED16, CODE_SHARED32, CODE_SHARED64 = 0x04, 0x05, 0x06, 0x14
CODE_BLOCK32, CODE_BLOCK64 = 0x08, 0x13
CODE_STRING8, CODE_STRING32, CODE_STRING64 = 0x09, 0x0A, 0x15
CODE_DOUBLE_BIG, CODE_DOUBLE_LITTLE = 0x0B, 0x0C
CODE_DOUBLE_ARRAY8_BIG, CODE_DOUBLE_ARRAY8_LITTLE = 0x0D, 0x0E
CODE_DOUBLE_ARRAY32_BIG, CODE_DOUBLE_ARRAY32_LITTLE = 0x0F, 0x07
CODE_DOUBLE_ARRAY64_BIG, CODE_DOUBLE_ARRAY64_LITTLE = 0x16, 0x17
CODE_CODEPOINTER, CODE_INFIXPOINTER = 0x10, 0x11
CODE_CUSTOM, CODE_CUSTOM_LEN, CODE_CUSTOM_FIXED = 0x12, 0x18, 0x19

DOUBLE_ARRAY_TAG = 254


class MarshalError(ValueError):
    pass


@dataclass(eq=False)
class Block:
    tag: int
    fields: list = field(default_factory=list)

    def __repr__(self) -> str:  # cycle-safe, shallow
        inner = ", ".join(
            f"Block(tag={f.tag}, n={len(f.fields)})" if isinstance(f, Block) else repr(f)
            for f in self.fields
        )
        return f"Block(tag={self.tag}, [{inner}])"


@dataclass(eq=False)
class FloatArray:
    values: list[float]


@dataclass
class Header:
    magic: int
    header_len: int
    data_len: int
    num_objects: int


def read_header(buf: bytes) -> Header:
    if len(buf) < 20:
        raise MarshalError("input too short for a marshal header")
    magic = struct.unpack_from(">I", buf, 0)[0]
    if magic == MAGIC_SMALL:
        data_len, num_objects = struct.unpack_from(">II", buf, 4)
        return Header(magic, 20, data_len, num_objects)
    if magic == MAGIC_BIG:
        data_len, num_objects = struct.unpack_from(">QQ", buf, 8)
        return Header(magic, 32, data_len, num_objects)
    if magic == MAGIC_COMPRESSED:
        raise MarshalError("compressed marshal data is not supported")
    raise MarshalError(f"bad magic number 0x{magic:08X}")


class _Reader:
    def __init__(self, buf: bytes, pos: int):
        self.buf, self.pos = buf, pos

    def take(self, n: int) -> bytes:
        if self.pos + n > len(self.buf):
            raise MarshalError(f"truncated input at offset {self.pos}")
        b = self.buf[self.pos:self.pos + n]
        self.pos += n
        return b

    def u8(self) -> int:
        return self.take(1)[0]

    def fmt(self, f: str) -> int | float:
        return struct.unpack(f, self.take(struct.calcsize(f)))[0]


def loads(buf: bytes) -> object:
    """Decode one marshalled value from the start of `buf` (bytes after it are ignored)."""
    value, _ = loads_with_size(buf)
    return value


def loads_with_size(buf: bytes) -> tuple[object, int]:
    """Decode one value; return it and the total number of bytes consumed."""
    hdr = read_header(buf)
    r = _Reader(buf, hdr.header_len)
    table: list = []
    # Each stack entry is (block_or_list, next_index). Values are written into
    # the slot `container[index]`; the root lives in a one-element list.
    root: list = [None]
    stack: list[list] = [[root, 0, 1]]  # [container, next index, end index]

    def store(v):
        top = stack[-1]
        container = top[0].fields if isinstance(top[0], Block) else top[0]
        container[top[1]] = v
        top[1] += 1

    while stack:
        top = stack[-1]
        if top[1] >= top[2]:
            stack.pop()
            continue
        code = r.u8()
        if code >= PREFIX_SMALL_BLOCK:
            tag, size = code & 0x0F, (code >> 4) & 0x07
            _new_block(tag, size, table, store, stack)
        elif code >= PREFIX_SMALL_INT:
            store(code & 0x3F)
        elif code >= PREFIX_SMALL_STRING:
            s = r.take(code & 0x1F)
            table.append(s)
            store(s)
        elif code == CODE_INT8:
            store(r.fmt(">b"))
        elif code == CODE_INT16:
            store(r.fmt(">h"))
        elif code == CODE_INT32:
            store(r.fmt(">i"))
        elif code == CODE_INT64:
            store(r.fmt(">q"))
        elif code in (CODE_SHARED8, CODE_SHARED16, CODE_SHARED32, CODE_SHARED64):
            ofs = {CODE_SHARED8: ">B", CODE_SHARED16: ">H", CODE_SHARED32: ">I", CODE_SHARED64: ">Q"}[code]
            off = r.fmt(ofs)
            if not 0 < off <= len(table):
                raise MarshalError(f"bad shared offset {off} at {r.pos}")
            store(table[len(table) - off])
        elif code in (CODE_BLOCK32, CODE_BLOCK64):
            hd = r.fmt(">I" if code == CODE_BLOCK32 else ">Q")
            _new_block(hd & 0xFF, hd >> 10, table, store, stack)
        elif code in (CODE_STRING8, CODE_STRING32, CODE_STRING64):
            n = r.fmt({CODE_STRING8: ">B", CODE_STRING32: ">I", CODE_STRING64: ">Q"}[code])
            s = r.take(n)
            table.append(s)
            store(s)
        elif code in (CODE_DOUBLE_BIG, CODE_DOUBLE_LITTLE):
            v = r.fmt(">d" if code == CODE_DOUBLE_BIG else "<d")
            table.append(v)
            store(v)
        elif code in (CODE_DOUBLE_ARRAY8_BIG, CODE_DOUBLE_ARRAY8_LITTLE,
                      CODE_DOUBLE_ARRAY32_BIG, CODE_DOUBLE_ARRAY32_LITTLE,
                      CODE_DOUBLE_ARRAY64_BIG, CODE_DOUBLE_ARRAY64_LITTLE):
            lenfmt = ">B" if code in (CODE_DOUBLE_ARRAY8_BIG, CODE_DOUBLE_ARRAY8_LITTLE) else (
                ">I" if code in (CODE_DOUBLE_ARRAY32_BIG, CODE_DOUBLE_ARRAY32_LITTLE) else ">Q")
            n = r.fmt(lenfmt)
            big = code in (CODE_DOUBLE_ARRAY8_BIG, CODE_DOUBLE_ARRAY32_BIG, CODE_DOUBLE_ARRAY64_BIG)
            fa = FloatArray([r.fmt(">d" if big else "<d") for _ in range(n)])
            table.append(fa)
            store(fa)
        elif code in (CODE_CUSTOM, CODE_CUSTOM_LEN, CODE_CUSTOM_FIXED):
            ident = bytearray()
            while (c := r.u8()) != 0:
                ident.append(c)
            if code == CODE_CUSTOM_LEN:
                r.take(4)  # 32-bit size (unused)
                r.take(8)  # 64-bit size (unused)
            name = ident.decode("ascii")
            if name == "_i":
                v = r.fmt(">i")
            elif name in ("_j", "_n"):
                if name == "_n":
                    kind = r.u8()
                    v = r.fmt(">i" if kind == 1 else ">q")
                else:
                    v = r.fmt(">q")
            else:
                raise MarshalError(f"unsupported custom block {name!r} at {r.pos}")
            table.append(v)
            store(v)
        elif code in (CODE_CODEPOINTER, CODE_INFIXPOINTER):
            raise MarshalError("code pointers / closures are not supported")
        else:
            raise MarshalError(f"unknown code 0x{code:02X} at offset {r.pos - 1}")

    consumed = r.pos - hdr.header_len
    if consumed != hdr.data_len:
        raise MarshalError(f"data length mismatch: header {hdr.data_len}, read {consumed}")
    if len(table) != hdr.num_objects:
        raise MarshalError(f"object count mismatch: header {hdr.num_objects}, read {len(table)}")
    return root[0], r.pos


def _new_block(tag: int, size: int, table: list, store, stack: list) -> None:
    b = Block(tag, [None] * size)
    if size > 0:
        table.append(b)  # atoms (size 0) are not entered in the sharing table
    store(b)
    if size > 0:
        stack.append([b, 0, size])


# --- helpers for interpreting decoded values --------------------------------

def is_none(v) -> bool:
    return v == 0 and isinstance(v, int)


def option(v):
    """OCaml `'a option`: None is the immediate 0; Some x is a tag-0 block of size 1."""
    if is_none(v):
        return None
    if isinstance(v, Block) and v.tag == 0 and len(v.fields) == 1:
        return v.fields[0]
    raise MarshalError(f"not an option value: {v!r}")


def to_list(v) -> list:
    """OCaml `'a list` (cons cells: tag-0 blocks [head, tail], [] = immediate 0)."""
    out = []
    while not is_none(v):
        if not (isinstance(v, Block) and v.tag == 0 and len(v.fields) == 2):
            raise MarshalError(f"not a list cell: {v!r}")
        out.append(v.fields[0])
        v = v.fields[1]
    return out


def unescape_ocaml_literal(lit: str) -> bytes:
    """Bytes of an OCaml string literal body (without the surrounding quotes).

    Handles \\ddd (decimal), \\xhh, \\o, \\n \\t \\r \\b \\\\ \\" \\' \\space.
    Non-ASCII source characters are encoded as UTF-8.
    """
    out = bytearray()
    i, n = 0, len(lit)
    simple = {"n": 10, "t": 9, "r": 13, "b": 8, "\\": 92, '"': 34, "'": 39, " ": 32}
    while i < n:
        c = lit[i]
        if c != "\\":
            out += c.encode("utf-8")
            i += 1
            continue
        nxt = lit[i + 1] if i + 1 < n else ""
        if nxt.isdigit():
            out.append(int(lit[i + 1:i + 4]))
            i += 4
        elif nxt == "x":
            out.append(int(lit[i + 2:i + 4], 16))
            i += 4
        elif nxt == "o":
            out.append(int(lit[i + 2:i + 5], 8))
            i += 5
        elif nxt in simple:
            out.append(simple[nxt])
            i += 2
        else:
            raise MarshalError(f"unknown escape \\{nxt} at {i}")
    return bytes(out)
