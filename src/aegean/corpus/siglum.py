"""Parse document sigla from any source into a canonical document key.

Sources write the same GORILA siglum differently:
- lineara.xyz:  "HT13", "HT122a", "KNZb<27>", "HTWa1845+1733", "KO(?)Zf2", "HT154ja"
- SigLA:        "HT 13", "HT 122a", "HT Wa 1019α", "HT 154A", "GO Wc 3 latus"
- Younger:      "HT 13", "KN Zb <27>", "KH Wc 2088+2089+fr", "LA Zb 1 (bis)", "PH(?) 31"

A canonical key is "SITE [Series ]NUMBER[+JOIN...][VARIANT]", e.g. "HT 13",
"HT Wa 1845+1733", "KN Zb <27>", "HT 113ter", "LA Zb 1bis". The side (a, b,
c...; Greek alpha, beta, gamma for nodule faces) is split off: sides are parts
of one document, not separate documents. Uppercase fragment letters
("HT 154A") stay in the key: GORILA numbers those fragments separately.

Parsing never discards information: the source's own ID is always kept next to
the key, and anything the parser does not recognise is reported (`parse`
returns None), never guessed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

SERIES = {"Wa", "Wb", "Wc", "Wd", "We", "Wf", "Wg", "Ws", "Wy", "Za", "Zb", "Zc", "Zd", "Ze", "Zf", "Zg"}
GREEK_SIDES = {"α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta"}

_RE = re.compile(
    r"""^(?P<site>[A-Z]{2,4})
        (?P<siteq>\(\?\))?
        \s*(?P<series>W[a-z]|Z[a-z])?
        \s*(?P<lt><)?(?P<num>\d+)
        (?P<join>(?:\+(?:\d+|frr?))*)
        (?P<variant>\s*(?:bis|ter)|\s*\(bis\)|[A-Z](?![a-z]{2}))?
        (?P<gt>>)?
        (?P<side>[a-z](?![a-z])|[αβγδ]|\s*-?latus)?
        (?P<tail>.*)$""",
    re.X,
)


@dataclass(frozen=True)
class Siglum:
    site: str
    series: str | None
    number: str  # digits, or "<digits>" (GORILA: document reported but lost / not seen)
    join: tuple[str, ...]  # further joined numbers ("59" in HT 42+59); "fr" = unnumbered fragment(s)
    variant: str | None  # bis | ter | fragment letter (HT 154A)
    side: str | None  # a | b | c ... | alpha | beta | gamma
    flags: tuple[str, ...] = field(default=())  # site_uncertain | id_uncertain | tail:<text>
    label: str | None = None  # a hand-assigned key for non-GORILA IDs (data/concordance/aliases.tsv)

    @property
    def key(self) -> str:
        """Canonical document key (no side)."""
        if self.label:
            return self.label
        s = self.site + (f" {self.series}" if self.series else "") + f" {self.number}"
        if self.join:
            s += "+" + "+".join(self.join)
        if self.variant:
            s += self.variant
        return s

    @property
    def match_key(self) -> str:
        """Key for cross-source matching: angle brackets dropped (sources disagree on them)."""
        return self.key.replace("<", "").replace(">", "")

    @property
    def components(self) -> tuple[str, ...]:
        """Numbered components ("HT 42", "HT 59" for HT 42+59), for clustering differently-joined records."""
        if self.label:
            return (self.label,)
        pre = self.site + (f" {self.series}" if self.series else "")
        nums = [self.number.strip("<>")] + [j for j in self.join if j.isdigit()]
        return tuple(f"{pre} {n}{self.variant or ''}" for n in nums)

    @property
    def lost(self) -> bool:
        return self.number.startswith("<")


def parse(raw: str) -> Siglum | None:
    """Parse a source ID; None if it is not a recognisable siglum."""
    s = raw.strip()
    flags = []
    if s.endswith("?") and not s.endswith("(?)"):
        flags.append("id_uncertain")
        s = s[:-1].strip()
    if s.endswith("(?)"):
        flags.append("id_uncertain")
        s = s[:-3].strip()
    s = s.replace(" (?)", "(?)").replace("(?) ", "(?)")
    m = _RE.match(s)
    if not m:
        return None
    if m.group("series") and m.group("series") not in SERIES:
        return None
    if m.group("siteq"):
        flags.append("site_uncertain")
    variant = m.group("variant")
    if variant:
        variant = variant.strip().strip("()")
    side = m.group("side")
    if side:
        side = side.strip().lstrip("-")
    if side in GREEK_SIDES:
        side = GREEK_SIDES[side]
    if m.group("lt") and not m.group("gt"):
        flags.append("unclosed_angle")
    tail = m.group("tail").strip()
    if tail:
        # Lineara writes fragment sides lowercase after a letter ("HT154ja"); SigLA "HT 154Ja".
        if re.fullmatch(r"[a-z]", tail) and side and len(side) == 1:
            variant, side = (variant or "") + side.upper(), tail
        elif re.fullmatch(r"[a-z]{2}", tail) and not side and not variant:
            variant, side = tail[0].upper(), tail[1]  # lineara "HT154ja" = SigLA "HT 154Ja"
        elif tail in (".",):
            flags.append("tail:.")
        else:
            flags.append(f"tail:{tail}")
    join = tuple(j for j in (m.group("join") or "").split("+") if j)
    number = f"<{m.group('num')}>" if m.group("lt") else m.group("num")
    return Siglum(m.group("site"), m.group("series"), number, join, variant or None, side, tuple(flags))


def from_label(label: str, flags: tuple[str, ...] = ()) -> Siglum:
    """A Siglum for a hand-assigned label; parsed normally when the label is a regular siglum."""
    p = parse(label)
    if p is not None and not p.flags:
        return Siglum(p.site, p.series, p.number, p.join, p.variant, p.side, flags)
    return Siglum(label.split()[0], None, "", (), None, None, flags + ("id_irregular",), label=label)
