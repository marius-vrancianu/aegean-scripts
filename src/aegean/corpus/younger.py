"""Read John G. Younger's Linear A transliterations (Academia.edu PDF, 2024).

Source: "Linear A Texts in phonetic transcription: Other Texts (not Haghia
Triada)", last update 28 March 2024, posted on Academia.edu after KU retired
people.ku.edu (DATA_SOURCES.md, data/raw/younger/README.md). Younger's Haghia
Triada file was not found on Academia, so HT documents are absent here.

The PDF carries meaning in its typography, which plain-text extraction loses,
so this reader works on characters with their font, colour and position
(pdfplumber):
- bold black = numbers (and the siglum in entry headings);
- plain black = statement words, logograms, fractions, row references;
- red = Younger's commentary; magenta = scribe / Schoep-type notes;
  blue = table column headers (used to locate the columns);
- underlined = "the reading of SIGN is doubtful" (Younger's conventions,
  section 3c of his introduction). Underlines are thin filled rectangles
  drawn under the characters.

Younger's text is L1: signs are given by conventional (Linear B) values,
e.g. KU-RO, with *nnn for signs without one. Mapping to sign IDs is A1.8.
Nothing here interprets readings; damage, doubt, erasure and restoration are
kept as separate per-sign fields, each as Younger marks it.

Epigraphic conventions (Younger, introduction 3c), as used in the tables:
  ]X  break before X;  X[  break after X  (his written definitions read the
      other way round; his usage, e.g. ARKH 1a.1 "]TA-PI", is the standard one)
  X underlined = doubtful reading;  [[ X ]] erased but legible;
  <X> once extant, now lost and supplied (restoration);
  -•- / [•] unidentified sign;  • word divider or transaction marker.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

SOURCE = "younger"

BLACK, RED, BLUE, MAGENTA, DARKRED, GREEN = "black", "red", "blue", "magenta", "darkred", "green"
LINE_TOL = 2.5  # pt: chars whose tops differ by less than this are on one line
GAP = 2.2  # pt: a horizontal gap wider than this starts a new word
UNDERLINE_MAX_H = 2.6  # pt: filled rectangles this thin are underlines
COLUMN_SLACK = 6.0  # pt: a word may start this far left of its column header
RULING_MIN_W = 200.0  # pt: a thin rectangle at least this wide is a ruled line, not an underline
RULING = "—RULING—"
SUBSCRIPT_MAX_SIZE = 9.0  # pt: body text is 12 (10.1 for headings/notes); subscripts are 7.9
SUBSCRIPT_DROP = 7.0  # pt: a subscript's top may sit this far below its line's top

SIGLUM_RE = re.compile(r"^[A-Z]{2,4}(?: [A-Z][a-z])? <?\d+>?[a-z]{0,2}(?:\+\d+[a-z]?)*$")
REF_RE = re.compile(r"^(?:[a-z]{1,3})?\.\d+(?:-\d+)?[a-z]?$|^[a-z]{1,3}\.\d+(?:-[a-z]?\.?\d+)?$|^[a-z]{1,3}$")
COLUMN_WORDS = {"side.line": "ref", "side/line": "ref", "statement": "statement", "logogram": "logogram",
                "number": "number", "numbe": "number", "fraction": "fraction", '"fraction"': "fraction",
                "no.": "impressions", "cms": "cms"}


# --- character layer -----------------------------------------------------------

@dataclass
class Char:
    text: str
    x0: float
    x1: float
    top: float
    bottom: float
    bold: bool
    italic: bool
    color: str
    size: float = 12.0
    underlined: bool = False


@dataclass
class Word:
    chars: list[Char]

    @property
    def text(self) -> str:
        return "".join(c.text for c in self.chars)

    @property
    def x0(self) -> float:
        return self.chars[0].x0

    @property
    def color(self) -> str:
        return self.chars[0].color

    @property
    def bold(self) -> bool:
        core = [c for c in self.chars if c.text.isalnum()]
        return bool(core) and all(c.bold for c in core)


@dataclass
class Line:
    page: int  # 1-based
    top: float
    words: list[Word]

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)

    @property
    def color(self) -> str:
        return self.words[0].color if self.words else BLACK


def _color(c) -> str:
    """Name of a character's fill colour. The PDF uses exact RGB values plus a
    near-black (0.04, 0.05, 0) on later pages; classify with tolerance."""
    v = c.get("non_stroking_color")
    if v is None:
        return BLACK
    if isinstance(v, (int, float)):
        v = (v, v, v)
    v = tuple(float(x) for x in v)
    if len(v) == 1:
        v = v * 3
    if len(v) != 3:
        return "other"
    r, g, b = v
    if max(v) < 0.2:
        return BLACK
    if r > 0.9 and g < 0.2 and b > 0.9:
        return MAGENTA
    if r > 0.9 and g < 0.2 and b < 0.2:
        return RED
    if r < 0.2 and g < 0.2 and b > 0.9:
        return BLUE
    if 0.4 < r < 0.6 and g < 0.2 and b < 0.2:
        return DARKRED
    if r < 0.2 and 0.4 < g < 0.6 and b < 0.2:
        return GREEN
    return "other"


def read_lines(pdf_path: Path) -> list[Line]:
    """All text lines of the PDF, in reading order, with per-character typography."""
    import pdfplumber  # optional dependency: pip install -e ".[pdf]"

    out: list[Line] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            thin = [r for r in page.rects if (r["bottom"] - r["top"]) <= UNDERLINE_MAX_H and r["x1"] > r["x0"]]
            unders = [r for r in thin if r["x1"] - r["x0"] < RULING_MIN_W]
            rulings = [r for r in thin if r["x1"] - r["x0"] >= RULING_MIN_W]
            chars = []
            for c in page.chars:
                font = c.get("fontname", "")
                ch = Char(c["text"], c["x0"], c["x1"], c["top"], c["bottom"],
                          bold="Bold" in font, italic="Italic" in font, color=_color(c), size=c.get("size", 12.0))
                if ch.text.strip():
                    mid = (ch.x0 + ch.x1) / 2
                    ch.underlined = any(r["x0"] - 0.5 <= mid <= r["x1"] + 0.5
                                        and ch.bottom - 3.0 <= r["top"] <= ch.bottom + 3.0 for r in unders)
                chars.append(ch)
            chars.sort(key=lambda c: (round(c.top), c.x0))
            rows: list[list[Char]] = []
            small = [ch for ch in chars if ch.size < SUBSCRIPT_MAX_SIZE]
            for ch in sorted((c for c in chars if c.size >= SUBSCRIPT_MAX_SIZE), key=lambda c: c.top):
                if rows and abs(rows[-1][0].top - ch.top) < LINE_TOL:
                    rows[-1].append(ch)
                else:
                    rows.append([ch])
            # Subscripts (RA2, PA3, TA2) are smaller glyphs set ~4 pt lower: attach
            # each to the line it hangs from, so "RA" + "2" read as one sign value.
            for ch in small:
                host = [r for r in rows if r[0].top - 1.0 <= ch.top <= r[0].top + SUBSCRIPT_DROP]
                if host:
                    host[-1].append(ch)
                else:
                    rows.append([ch])
            rows.sort(key=lambda r: r[0].top)
            for row in rows:
                row.sort(key=lambda c: c.x0)
                words: list[Word] = []
                cur: list[Char] = []
                last_x1 = None
                for ch in row:
                    if not ch.text.strip():
                        if cur:
                            words.append(Word(cur))
                            cur = []
                        last_x1 = ch.x1
                        continue
                    if cur and last_x1 is not None and ch.x0 - last_x1 > GAP:
                        words.append(Word(cur))
                        cur = []
                    cur.append(ch)
                    last_x1 = ch.x1
                if cur:
                    words.append(Word(cur))
                if words:
                    out.append(Line(pno, row[0].top, words))
            # Ruled lines drawn across a table (e.g. KH 3) are graphics, not text:
            # emit them as lines holding RULING so they keep their place in the text.
            for r in rulings:
                ch = Char(RULING, r["x0"], r["x1"], r["top"] - 8.0, r["bottom"], False, False, BLACK)
                out.append(Line(pno, r["top"] - 8.0, [Word([ch])]))
    return _sort_by_page(out)


def _sort_by_page(lines: list[Line]) -> list[Line]:
    return sorted(lines, key=lambda l: (l.page, l.top))


# --- source records ----------------------------------------------------------------

@dataclass
class Sign:
    """One sign of a statement word, with Younger's per-sign marks."""
    value: str  # L1 transliteration value as printed, e.g. "KU", "*301", "PA3"; "•" for an unidentified sign
    doubtful: bool  # underlined ("the reading of SIGN is doubtful")
    break_before: str  # "" | "]" (break directly before) | "]-" (break, word continues beyond it)
    break_after: str  # "" | "[" | "-["
    erased: bool  # inside [[ ]]
    restored: bool  # inside < > ("once extant, now lost and supplied")
    conjectural: bool  # printed in green: Younger's own conjectural fill of a lacuna
    unidentified: bool  # "•" used as a sign slot (-•-, [•])


@dataclass
class Group:
    """A sign-group (word) of the statement column, or a free-text inscription line."""
    raw: str  # as printed (underlining is not visible in raw; see signs)
    signs: list[Sign]
    divider_after: bool  # followed by "•"
    lacuna_dots: int | None = None  # "[ • • • ]": a lacuna with Younger's estimate of lost signs (no signs)
    doubtful: bool = False  # for sign-less groups ("•[" underlined)


@dataclass
class Row:
    ref: str | None  # side.line as printed, e.g. "a.1", ".3-4"; None for unreferenced lines
    statement: list[Group]
    logogram: str | None  # raw cell text, e.g. "OVIS+SI {*512}", "*303+D {*624}"
    logogram_doubtful: bool
    number: str | None  # raw cell text, e.g. "2", "1[ ]", "]8"
    number_doubtful: bool
    fraction: str | None  # raw cell text, e.g. "J", "E J", "B B", "L L2"
    fraction_doubtful: bool
    other: list[str] = field(default_factory=list)  # e.g. "supra mutila", "deest", "vacant", ruled line "____"
    extra: dict[str, str] = field(default_factory=dict)  # roundels/nodules: "impressions", "cms" (raw text)
    raw: str = ""


@dataclass
class Document:
    id: str
    source: str
    page: int
    header: str  # metadata text after the siglum, as printed (support, museum no., GORILA ref, context)
    annotations: list[str]  # magenta lines: scribe, Schoep 2002 type
    heading: str  # the bold heading as printed, e.g. "PH(?) 31", "KH Wa 1003, 1004"
    joint_ids: list[str]  # further sigla Younger prints in the same entry heading
    flags: list[str]  # site_uncertain | range | irregular_siglum | cross_reference
    layout: str  # "table" or "text"
    rows: list[Row]  # tables: one per printed row; texts: one per text line (statement only)
    notes: list[str]  # Younger's commentary (red)
    commentary_rows: list[Row] = field(default_factory=list)  # data-like rows printed after commentary began:
    # Younger's reconstructions (e.g. PH 31, green fills "to match the totals"). Never transcription.

    def to_dict(self) -> dict:
        return asdict(self)


# --- parsing --------------------------------------------------------------------------

SITE_RE = re.compile(r"^[A-Z]{2,4}(?:\(\?\))?[,:]?$")
HEADING_MAX_X = 80.0  # pt: entry headings start at the left margin (x ~ 72)
BODY_MIN_X = 74.0  # pt: heading continuation lines sit at the margin; body lines are indented


def _heading_lead(line: Line) -> list[str]:
    """Leading bold words of a line, allowing an unbolded "(?)" / "?" between bold words."""
    out: list[str] = []
    ws = line.words
    for k, w in enumerate(ws):
        if w.bold:
            out.append(w.text)
        elif w.text in ("(?)", "?") and k + 1 < len(ws) and ws[k + 1].bold and out:
            out.append(w.text)
        else:
            break
    return out


def _is_heading(line: Line) -> str | None:
    """The printed heading if `line` starts a document entry, else None.

    An entry heading is black, starts at the left margin, and its bold lead
    begins with a site abbreviation (2-4 capitals, optionally "(?)"). Younger's
    headings are irregular ("PH(?) 31", "KH Wa 1006-1008", "LA Zb 1 (bis)",
    "PE Ws", "THE small tablet fragment 1"), so the printed form is kept and
    normalised separately by `normalise_id`.
    """
    # Headings are black, or blue where the web original hyperlinked them (KH 100).
    # Blue column headers are never bold, so the bold-siglum test still separates them.
    if line.color not in (BLACK, BLUE) or not line.words or line.words[0].x0 > HEADING_MAX_X:
        return None
    lead = _heading_lead(line)
    if len(lead) < 2 or not SITE_RE.match(lead[0]):
        return None
    return " ".join(lead).rstrip(",:").strip()


def normalise_id(heading: str) -> tuple[str, list[str], list[str]]:
    """(id, joint_ids, flags) from a printed heading.

    "PH(?) 31" -> ("PH 31", [], ["site_uncertain"]);
    "KH Wa 1003, 1004" -> ("KH Wa 1003", ["KH Wa 1004"], []);
    "KH Wa 1006-1008" -> ("KH Wa 1006", ["KH Wa 1007", "KH Wa 1008"], ["range"]).
    """
    flags = []
    h = heading
    if "(?)" in h or re.match(r"^[A-Z]{2,4} \?", h):
        flags.append("site_uncertain")
        h = h.replace("(?)", " ")
        h = re.sub(r"^([A-Z]{2,4}) \? ", r"\1 ", h)
    h = re.sub(r"\s+", " ", h).strip()
    parts = [p.strip() for p in h.split(",") if p.strip()]
    first = parts[0]
    joint = []
    m = re.match(r"^(.*\D)(\d+)-(\d+)$", first)
    if m and 0 < int(m.group(3)) - int(m.group(2)) < 50:
        prefix, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        first = f"{prefix}{a}"
        joint = [f"{prefix}{k}" for k in range(a + 1, b + 1)]
        flags.append("range")
    prefix = first.rsplit(" ", 1)[0]
    for p in parts[1:]:
        joint.append(p if re.match(r"^[A-Z]{2,4} ", p) else f"{prefix} {p}")
    if not SIGLUM_RE.match(first):
        flags.append("irregular_siglum")
    return first, joint, flags


def _columns(line: Line) -> dict[str, float] | None:
    if line.color != BLUE:
        return None
    cols = {}
    for w in line.words:
        key = COLUMN_WORDS.get(w.text.lower())
        if key and key not in cols:
            cols[key] = w.x0
    return cols if "statement" in cols else None


def _column_of(x: float, cols: dict[str, float]) -> str:
    best, best_x = "ref", -1.0
    for name, cx in cols.items():
        if cx - COLUMN_SLACK <= x and cx > best_x:
            best, best_x = name, cx
    return best


def parse_group(word: Word) -> Group:
    """Split a printed sign-group into signs, carrying per-character marks into per-sign fields.

    Handles "]-NU-TI" / "]TA-PI" (break before, with / without a lost part of
    the word), "ZA-[" / "A-RA[" (break after), "[[ X ]]" (erased), "<X>"
    (restored), "-•-" / "[•]" (unidentified sign), "•" (divider), subscript
    values ("RA2", printed with a smaller "2"), underline (doubt) and green
    (Younger's conjecture).
    """
    text = word.text
    chars = word.chars
    signs: list[Sign] = []
    erased = restored = False
    pend_break = ""
    divider_after = False
    i, n = 0, len(text)

    def mark(j0, j1):
        span = chars[j0:j1]
        return any(c.underlined for c in span), any(c.color == GREEN for c in span)

    while i < n:
        if text.startswith("[[", i):
            erased, i = True, i + 2
            continue
        if text.startswith("]]", i):
            erased, i = False, i + 2
            continue
        ch = text[i]
        if ch == "<":
            restored, i = True, i + 1
            continue
        if ch == ">":
            restored, i = False, i + 1
            continue
        if ch == "]":
            pend_break = "]-" if text.startswith("]-", i) else "]"
            i += len(pend_break)
            continue
        if text.startswith("[•]", i):
            d, g = mark(i, i + 3)
            signs.append(Sign("•", d, pend_break, "", erased, restored, g, True))
            pend_break, i = "", i + 3
            continue
        if text.startswith("-[•]", i):
            i += 1  # "A-TA-NA-[•]": hyphen, then an unidentified sign
            continue
        if ch == "[" or text.startswith("-[", i):
            if signs:
                signs[-1].break_after = "-[" if ch == "-" else "["
            i += 2 if ch == "-" else 1
            continue
        if ch == "-":
            i += 1
            continue
        if ch == "•":
            slot = (i + 1 < n and text[i + 1] == "-") or (i > 0 and text[i - 1] == "-")
            if slot:
                d, g = mark(i, i + 1)
                signs.append(Sign("•", d, pend_break, "", erased, restored, g, True))
                pend_break = ""
            else:
                divider_after = True
            i += 1
            continue
        j = i
        while j < n and text[j] not in "-[]<>•":
            j += 1
        d, g = mark(i, j)
        signs.append(Sign(text[i:j], d, pend_break, "", erased, restored, g, False))
        pend_break, i = "", j
    return Group(raw=text, signs=signs, divider_after=divider_after)


def _cell_text(words: list[Word]) -> str | None:
    t = " ".join(w.text for w in words).strip()
    return t or None


def _doubtful(words: list[Word]) -> bool:
    return any(c.underlined for w in words for c in w.chars)


def _statement_groups(words: list[Word]) -> list[Group]:
    """Sign-groups of a statement cell or text line.

    A run of standalone "•" between a token ending in "[" and a token starting
    with "]" is Younger's estimate of lost signs in a lacuna ("I-PI-NA-MA [ • • • ]I-KU"),
    not a series of word dividers.
    """
    groups: list[Group] = []
    k, n = 0, len(words)
    while k < n:
        w = words[k]
        txt = w.text
        opens = txt.endswith("[") or (txt == "[")
        if opens:
            j = k + 1
            dots = 0
            while j < n and words[j].text == "•":
                dots += 1
                j += 1
            if dots and j < n and words[j].text.startswith("]"):
                if txt != "[":
                    groups.append(parse_group(w))
                groups.append(Group(raw="[ " + " ".join("•" * 1 for _ in range(dots)) + " ]", signs=[],
                                    divider_after=False, lacuna_dots=dots))
                # A bare "]" closes the lacuna; a "]X" token is parsed next, with its break_before.
                k = j + 1 if words[j].text == "]" else j
                continue
        if txt == "•":
            if groups:
                groups[-1].divider_after = True
            k += 1
            continue
        if txt in ("]", "[") and groups:
            if txt == "[" and groups[-1].signs and not groups[-1].signs[-1].break_after:
                groups[-1].signs[-1].break_after = "["
            groups[-1].raw += txt
            k += 1
            continue
        if re.fullmatch(r"[\[\]]?•[\[\]]?", txt):  # "•[", "]•": a divider/dot at a break
            groups.append(Group(raw=txt, signs=[], divider_after=False,
                                doubtful=any(c.underlined for c in w.chars)))
            k += 1
            continue
        groups.append(parse_group(w))
        k += 1
    return groups


_OTHER_RE = re.compile(r"^—RULING—$|^(supra|infra)\s+mutila|^deest|^vacant|^_{3,}|^[-|_ ]{5,}$|^vest\.$|^separate|^fragment", re.I)
# A transliteration-like word: signs, numbers, logograms (OVISf, VINa, *303+D), {*624}, brackets, dividers.
_TRANSLIT_RE = re.compile(r"^[\[\]<>•\-A-Z0-9*+/{}?|:.,;()]+[a-z]{0,4}[\]\[}]*$")


def _is_prose(words: list[Word]) -> bool:
    """True for a line of English (seal descriptions, remarks) rather than transliteration."""
    texts = [w.text for w in words if w.text not in ("•", "&")]
    if not texts:
        return False
    # Transliteration never contains an all-lowercase English word of 3+ letters
    # (apart from the epigraphic terms caught by _OTHER_RE).
    if any(re.fullmatch(r"[a-z]{3,}[.,;:)]?", x) and x.rstrip(".,;:)") not in _EPIGRAPHIC for x in texts):
        return True
    prose = sum(1 for x in texts if not _TRANSLIT_RE.match(x))
    return prose / len(texts) > 0.5


_EPIGRAPHIC = {"vest", "vacat", "vacant", "deest", "supra", "infra", "mutila", "bis"}


def _table_row(line: Line, cols: dict[str, float]) -> Row:
    cells: dict[str, list[Word]] = {k: [] for k in ("ref", "statement", "logogram", "number", "fraction",
                                                     "impressions", "cms")}
    for w in line.words:
        cells[_column_of(w.x0, cols)].append(w)
    extra = {k: v for k in ("impressions", "cms") if (v := _cell_text(cells[k]))}
    ref_words = cells["ref"]
    ref = ref_words[0].text if ref_words and REF_RE.match(ref_words[0].text) else None
    other = []
    if ref is None and ref_words:
        cells["statement"] = ref_words + cells["statement"]
    elif ref_words[1:]:
        cells["statement"] = ref_words[1:] + cells["statement"]
    stmt = cells["statement"]
    if stmt and (_OTHER_RE.match(" ".join(w.text for w in stmt)) or _is_prose(stmt)):
        other.append(" ".join(w.text for w in stmt))
        stmt = []
    # Bold digits are numbers wherever they sit; plain letters right of the
    # number column are fractions (Younger prints numbers bold).
    num_words = [w for w in cells["number"] + cells["fraction"] if w.bold or re.fullmatch(r"[\[\]\d ]+", w.text)]
    frac_words = [w for w in cells["number"] + cells["fraction"] if w not in num_words]
    return Row(
        ref=ref,
        statement=_statement_groups(stmt),
        logogram=_cell_text(cells["logogram"]), logogram_doubtful=_doubtful(cells["logogram"]),
        number=_cell_text(num_words), number_doubtful=_doubtful(num_words),
        fraction=_cell_text(frac_words), fraction_doubtful=_doubtful(frac_words),
        other=other, extra=extra, raw=line.text,
    )


def _text_row(line: Line) -> Row:
    words = list(line.words)
    ref = None
    first = words[0].text if words else ""
    # Line / side references of free-text entries: ".1:", "a.2:", "a:", ".b:", "a+g:", or ".1" at the margin.
    if words and (re.fullmatch(r"\.?[a-z]{1,3}(?:\+[a-z])?(?:\.?\d+(?:-\d+)?)?[a-z]?:|\.\d+(?:-\d+)?[a-z]?:", first)
                  or REF_RE.match(first) and words[0].x0 < 90 and "." in first):
        ref = words[0].text.rstrip(":")
        words = words[1:]
    other = []
    joined = " ".join(w.text for w in words)
    if words and (_OTHER_RE.match(joined) or _is_prose(words)):
        other.append(joined)
        words = []
    return Row(ref=ref, statement=_statement_groups(words), logogram=None, logogram_doubtful=False,
               number=None, number_doubtful=False, fraction=None, fraction_doubtful=False,
               other=other, raw=line.text)


def parse_lines(lines: list[Line]) -> list[Document]:
    docs: list[Document] = []
    cur: Document | None = None
    cols: dict[str, float] | None = None
    in_body = in_commentary = False
    for ln in lines:
        heading = _is_heading(ln)
        if heading:
            doc_id, joint, flags = normalise_id(heading)
            lead = _heading_lead(ln)
            rest = " ".join(w.text for w in ln.words[len(lead):]).lstrip(", ").strip()
            if lead[-1].endswith(":") and rest.lower().startswith("see "):
                flags.append("cross_reference")
            cur = Document(id=doc_id, source=SOURCE, page=ln.page, header=rest, annotations=[],
                           heading=heading, joint_ids=joint, flags=flags, layout="text", rows=[], notes=[])
            docs.append(cur)
            cols, in_body, in_commentary = None, False, False
            continue
        if cur is None:
            continue
        if ln.color == BLACK and _is_site_title(ln):
            cur, cols = None, None
            continue
        if ln.color == MAGENTA:
            cur.annotations.append(ln.text)
            in_body = True
            continue
        if ln.color == RED:
            cur.notes.append(ln.text)
            in_body, in_commentary = True, True
            continue
        c = _columns(ln)
        if c:
            cols, in_body = c, True
            if not in_commentary:
                cur.layout = "table"
            continue
        if ln.color == BLUE:
            continue
        if ln.color != BLACK:  # dark red / green / other: kept as notes, colour-tagged
            cur.notes.append(f"[{ln.color}] {ln.text}")
            continue
        if _is_site_title(ln):
            cur, cols = None, None
            continue
        if not in_body and cols is None and ln.words[0].x0 < BODY_MIN_X:
            cur.header = (cur.header + " " + ln.text).strip()  # wrapped metadata line (at the margin)
            continue
        in_body = True
        row = _table_row(ln, cols) if cols else _text_row(ln)
        (cur.commentary_rows if in_commentary else cur.rows).append(row)
    return docs


def _is_site_title(ln: Line) -> bool:
    """Centred capitalised site names between entries: "KNOSSOS", "HAGHIOS STEPHANOS", "TEL HAROR, ISRAEL"."""
    t = ln.text.strip()
    if t == RULING:
        return False
    letters = [c for c in t if c.isalpha()]
    return (len(letters) >= 4 and all(c.isupper() for c in letters) and ln.words[0].x0 > 150
            and not any(c.isdigit() for c in t) and "-" not in t and "+" not in t)


# --- held-out filter and entry point ------------------------------------------------

def load_documents(pdf_path: Path, heldout: dict[str, set[str]] | None = None) -> list[Document]:
    """All non-held-out entries, in document order."""
    from aegean.corpus.heldout import heldout_keys, is_heldout_siglum

    keys = heldout_keys(heldout)
    return [d for d in parse_lines(read_lines(pdf_path)) if not is_heldout_siglum(d.id, keys)]
