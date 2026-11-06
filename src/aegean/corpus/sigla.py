"""Read the SigLA database (sigla.phis.me/database.js) into raw OCaml values.

SigLA (Salgarella & Castellan; CC BY-NC-SA 4.0, see DATA_SOURCES.md) is a
static site whose OCaml/js_of_ocaml front end loads `database.js`. That file
defines two JavaScript variables, `signs` and `data`. Each holds an OCaml
string literal (inside a single-quoted JS string) whose bytes are an OCaml
`Marshal` value. This module undoes the two layers of quoting and unmarshals.

Record layouts are not documented by SigLA; their interpretation into the
corpus schema is a separate step and every field mapping there must be
checked against the rendered site (A1.4 / A1.7).
"""
from __future__ import annotations

import re
from pathlib import Path

from aegean.corpus import ocaml_marshal as om

SOURCE = "sigla"
_VAR_RE = re.compile(r"var\s+(\w+)\s*=\s*'")


def _js_single_quoted(text: str, start: int) -> tuple[str, int]:
    """Value of the JS single-quoted string whose opening quote is at text[start-1]."""
    out, i = [], start
    js_simple = {"\\": "\\", "'": "'", '"': '"', "n": "\n", "t": "\t", "r": "\r", "0": "\0"}
    while True:
        c = text[i]
        if c == "'":
            return "".join(out), i + 1
        if c == "\\":
            nxt = text[i + 1]
            if nxt in js_simple:
                out.append(js_simple[nxt])
                i += 2
            elif nxt == "u":
                out.append(chr(int(text[i + 2:i + 6], 16)))
                i += 6
            elif nxt == "x":
                out.append(chr(int(text[i + 2:i + 4], 16)))
                i += 4
            else:
                raise ValueError(f"unsupported JS escape \\{nxt} at {i}")
        else:
            out.append(c)
            i += 1


def extract_variables(text: str) -> dict[str, bytes]:
    """{variable name: marshalled bytes} for every `var x = '"..."'` in database.js."""
    out: dict[str, bytes] = {}
    for m in _VAR_RE.finditer(text):
        js_value, _ = _js_single_quoted(text, m.end())
        if not (js_value.startswith('"') and js_value.endswith('"')):
            raise ValueError(f"variable {m.group(1)} does not hold an OCaml string literal")
        out[m.group(1)] = om.unescape_ocaml_literal(js_value[1:-1])
    return out


def load_raw(path: Path) -> dict[str, object]:
    """{variable name: decoded OCaml value}. Raises on any decoding inconsistency."""
    blobs = extract_variables(path.read_text(encoding="utf-8"))
    out = {}
    for name, blob in blobs.items():
        value, used = om.loads_with_size(blob)
        if used != len(blob):
            raise om.MarshalError(f"{name}: {len(blob) - used} trailing bytes after the marshalled value")
        out[name] = value
    return out
