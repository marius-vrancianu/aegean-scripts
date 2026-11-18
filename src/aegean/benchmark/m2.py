"""Method M2: sound-class skeleton matching with Dolgopolsky's classes (plan A5.3).

A generic look-alike matcher, with none of M1's claim-specific licences (no
affix menus, no unwritten radicals, no vowel read as a laryngeal). It stands
for the many proposals that compare a script's words with a language's words
"by sound" after merging similar consonants.

1. A sign-group is read in conventional Linear B values (L1) and becomes a
   string of Dolgopolsky consonant classes (`SIGN_DOLGO`): each sign gives the
   class of its consonant(s); a pure vowel sign gives nothing. A sign with no
   Linear B value (*301, *56 ...) makes the group not eligible.
2. A lexicon form is a string in the same classes, converted from the
   language's own sounds by the lexicon loader (`aegean.benchmark.lexicons`,
   the `*-dolgo` lexicons).
3. A sign-group matches if some lexicon form is within normalised edit distance
   `max_distance` of it: Levenshtein distance divided by the longer length.
   The value is fixed in `M2Rules` and in the hypothesis that runs M2.

Dolgopolsky's classes (Dolgopolsky 1986), as LingPy's DOLGO model gives them
(List 2012; LingPy 2.6.13, `lingpy/data/models/dolgo/converter`, read for its
class table only; LingPy is GPL-3.0 and is not a dependency):

| Class | Sounds |
|---|---|
| P | labial stops and fricatives except v: p b f (ɸ β) |
| T | dental stops and fricatives: t d θ ð |
| S | sibilant fricatives: s z ʃ ʒ |
| K | velar and uvular stops and fricatives, and all affricates: k g q x ɣ, ts dz tʃ dʒ |
| M | m |
| N | n ŋ ɲ |
| R | liquids: r l |
| W | w v |
| J | j |
| H | laryngeals: ʔ h ħ ʕ |

Vowels are dropped. Unlike M1, d and t are one class (T), affricates are K, and
v is W.

Linear B values (`SIGN_DOLGO`): the consonant letter of the conventional value
gives the class (q, the labiovelar series, is K; z, whose sound is uncertain, is
taken at its letter value, S); a2 is *ha* (H); signs with two consonants give
both (dwe TW, nwa NW, pte PT, swa SW, twe TW); ta2 (*tya*) TJ; ra2 and ro2
(*rya*, *ryo*) RJ; ra3 (*rai*) R; pu2 (*phu*) P; a3 (*ai*) and au are vowels.
These are the conventional Linear B values (Unicode names), not claims about
Minoan sounds.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any

from aegean.benchmark.interface import Lexicon, Match, Method, SignGroup

DOLGO_CLASSES = "PTSKMNRWJH"

_CV = {"": "", "D": "T", "J": "J", "K": "K", "M": "M", "N": "N", "P": "P", "Q": "K", "R": "R", "S": "S",
       "T": "T", "W": "W", "Z": "S"}
SIGN_DOLGO: dict[str, str] = {}
for _v in ("A", "E", "I", "O", "U"):
    for _c, _cls in _CV.items():
        SIGN_DOLGO[_c + _v] = _cls
SIGN_DOLGO.update({"A2": "H", "A3": "", "AU": "", "DWE": "TW", "DWO": "TW", "NWA": "NW", "PTE": "PT",
                   "PU2": "P", "RA2": "RJ", "RA3": "R", "RO2": "RJ", "SWA": "SW", "SWI": "SW", "TA2": "TJ",
                   "TWE": "TW", "TWO": "TW"})


@dataclass(frozen=True)
class M2Rules:
    """Every free parameter of M2."""
    # Normalised Levenshtein distance allowed. 1/4 is the strictest value that allows any edit at the lexicons'
    # form lengths (2-4 classes: one edit once the longer string has 4 classes). Chosen before any run on Linear A
    # or the control, on uniform random strings of Linear B values: 0 allows no edit at all, and 1/3 saturates
    # (0.93-0.99 of two- and three-class skeletons match any of the three lexicons).
    max_distance: float = 0.25
    min_skeleton: int = 2      # a sign-group needs at least this many consonant classes to be eligible
    min_group: int = 2

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _neighbourhood(s: str, depth: int) -> dict[str, int]:
    """Every string within `depth` edits of s (alphabet DOLGO_CLASSES), with its edit distance."""
    out = {s: 0}
    frontier = {s}
    for d in range(1, depth + 1):
        nxt = set()
        for x in frontier:
            for i in range(len(x) + 1):
                for c in DOLGO_CLASSES:
                    nxt.add(x[:i] + c + x[i:])          # insertion
                if i < len(x):
                    nxt.add(x[:i] + x[i + 1:])          # deletion
                    for c in DOLGO_CLASSES:
                        if c != x[i]:
                            nxt.add(x[:i] + c + x[i + 1:])  # substitution
        nxt = {y for y in nxt if y not in out}
        for y in nxt:
            out[y] = d
        frontier = nxt
    return out


class M2(Method):
    """Dolgopolsky sound-class skeleton matching behind the benchmark interface."""

    name = "M2"
    layer = "L1"

    def __init__(self, rules: M2Rules | None = None) -> None:
        self.rules = rules or M2Rules()
        if not 0 <= self.rules.max_distance < 1:
            raise ValueError("max_distance must be in [0, 1)")
        self._reach = lru_cache(maxsize=None)(self._reach_uncached)

    def skeleton(self, group: SignGroup) -> str | None:
        """The group's Dolgopolsky string, or None if a sign has no Linear B value."""
        out = []
        for s in group:
            c = SIGN_DOLGO.get(s.upper())
            if c is None:
                return None
            out.append(c)
        return "".join(out)

    def eligible(self, group: SignGroup) -> bool:
        sk = self.skeleton(group)
        return len(group) >= self.rules.min_group and sk is not None and len(sk) >= self.rules.min_skeleton

    def allowed(self, a: str, b: str) -> bool:
        return levenshtein(a, b) <= self.rules.max_distance * max(len(a), len(b))

    def _reach_uncached(self, group: SignGroup) -> frozenset[str]:
        """Every string the group matches, whatever the lexicon (lexicon forms have at most 4 classes here,
        but the set is exact for any length up to the edit bound)."""
        sk = self.skeleton(group)
        if sk is None or not self.eligible(group):
            return frozenset()
        # d <= θ·max(len) and |len difference| <= d bound the search depth.
        depth = 0
        while (depth + 1) <= self.rules.max_distance * (len(sk) + depth + 1):
            depth += 1
        return frozenset(x for x, d in _neighbourhood(sk, depth).items()
                         if d <= self.rules.max_distance * max(len(sk), len(x)) and x)

    def skeletons(self, group: SignGroup) -> frozenset[str]:
        """All lexicon forms that would match the group. Its size is the group's permissiveness."""
        return self._reach(group)

    def match(self, group: SignGroup, prepared: frozenset[str]) -> Match | None:
        if not self.eligible(group):
            return None
        sk = self.skeleton(group)
        best = None
        for f in prepared:
            if self.allowed(sk, f):
                d = levenshtein(sk, f)
                if best is None or (d, f) < best:
                    best = (d, f)
        return None if best is None else Match(group, best[1], {"skeleton": sk, "distance": best[0]})

    def hits(self, groups: list[SignGroup], prepared: frozenset[str]) -> list[bool]:
        return [self.eligible(g) and not self.skeletons(g).isdisjoint(prepared) for g in groups]

    def degrees_of_freedom(self) -> dict[str, Any]:
        return {
            "sign_value_mergers": {"classes": "Dolgopolsky (10 consonant classes)", "merged": "voicing; place within "
                                   "class; t/d; affricates with velars; v with w; r with l (also Linear B r)"},
            "vowel_signs": {"readings_per_sign": 1, "note": "a pure vowel sign gives nothing; a2 is H"},
            "unwritten_radicals": {"note": "none, except through the edit distance"},
            "doubled_signs": {"collapse": False},
            "affix_menus": {"prefixes": 0, "suffixes": 0},
            "edit_distance": {"max_normalised": self.rules.max_distance},
            "languages_pooled": {"count": 1, "note": "set by the lexicon passed in, not by the method"},
        }
