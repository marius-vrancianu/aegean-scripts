"""Method M1: the Finding 001 root matcher (di Mino 2026, "Ya Diktu"), ported (plan A5.12).

Built from `experiments/finding-001/original/nulltest.py`, which stays as the
record of the 2026-10-28 run. The port keeps that script's behaviour exactly
(tests/test_benchmark_m1.py runs both on the same inputs) and changes only its
shape: no module-level state, no file access, rules in a dataclass.

What the method does. A sign-group is read in conventional Linear B values
(L1) and compared with consonantal roots of a Semitic lexicon:

1. optionally strip one prefix and one suffix from fixed menus;
2. the remaining core must be 1 to 4 signs; adjacent identical signs collapse;
3. each sign gives its consonant *class* (stops, sibilants and liquids
   merged); a pure-vowel sign gives either a laryngeal (class H) or nothing;
4. a two-consonant skeleton may take one unwritten weak radical (H, W or J)
   in any position;
5. the result is a hit if a skeleton of 2 to 4 consonants is in the lexicon,
   where every lexicon root is also allowed with S read as T and with D and T
   interchanged.

These licences are the paper's, as encoded for Finding 001; that encoding is
approximate (Finding 001, Limitations). Consonant classes: H laryngeal,
P labial stop, K velar stop, D, T, S sibilant, R liquid, M, N, W, J.

Known oddities kept from the original, because changing them would make this
a different method from the one Finding 001 tested:
- the vowel-sign list has A3 and AI but not A2, so a group containing A2 is
  not eligible;
- signs without a Linear B value (*56, *79 ...) make a group not eligible,
  except *301, which the paper reads as a nasal.
"""
from __future__ import annotations

import itertools
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

from aegean.benchmark.interface import Lexicon, Match, Method, SignGroup

UNKNOWN = "?"

PREFIXES: tuple[SignGroup, ...] = (
    ("A",), ("TA",), ("JA",), ("I",), ("U", "NA"), ("NA",), ("WA",), ("RA",),
    ("A", "TA"), ("TA", "NA"), ("JA", "TA"), ("A", "NA"),
)
SUFFIXES: tuple[SignGroup, ...] = (
    ("ME",), ("MA",), ("TU",), ("TI",), ("TE",), ("NU",), ("JA",), ("SE",), ("I",), ("KA",), ("NA",), ("NE",),
    ("TI", "NU"), ("U", "TI", "NU"), ("MI", "NA"), ("TE", "TE"),
)
VOWEL_SIGNS: tuple[str, ...] = ("A", "E", "I", "O", "U", "AU", "A3", "AI")
# Signs whose class is not the class of their first letter, or that are not plain CV signs.
SPECIAL_SIGNS: dict[str, str] = {
    "*301": "N",
    "PU2": "P", "PA3": "P", "RA2": "R", "RO2": "R", "RA3": "R", "TA2": "T", "TWE": "T", "TWO": "T",
    "DWE": "D", "DWO": "D", "NWA": "N", "SWA": "S", "SWI": "S", "PTE": "P",
}
INITIAL_CLASS: dict[str, str] = {
    "J": "J", "W": "W", "Q": "K", "K": "K", "P": "P", "T": "T", "D": "D", "S": "S", "Z": "S", "R": "R",
    "M": "M", "N": "N",
}
# Lexicon-side interchanges: a root letter may be read as any letter of its set.
INTERCHANGES: dict[str, str] = {"S": "ST", "D": "DT", "T": "DT"}
WEAK_RADICALS = "HWJ"


@dataclass(frozen=True)
class M1Rules:
    """Every free parameter of M1. The defaults are the Finding 001 encoding."""
    prefixes: tuple[SignGroup, ...] = PREFIXES
    suffixes: tuple[SignGroup, ...] = SUFFIXES
    vowel_signs: tuple[str, ...] = VOWEL_SIGNS
    special_signs: tuple[tuple[str, str], ...] = tuple(sorted(SPECIAL_SIGNS.items()))
    initial_class: tuple[tuple[str, str], ...] = tuple(sorted(INITIAL_CLASS.items()))
    interchanges: tuple[tuple[str, str], ...] = tuple(sorted(INTERCHANGES.items()))
    weak_radicals: str = WEAK_RADICALS
    laryngeal: str = "H"
    collapse_doubled: bool = True
    min_core: int = 1
    max_core: int = 4
    min_skeleton: int = 2
    max_skeleton: int = 4
    min_group: int = 2

    @classmethod
    def from_json(cls, path: Path) -> "M1Rules":
        """Rules from a JSON file with any subset of the fields; the rest keep the Finding 001 values.

        Menus are lists of sign-groups written "U-NA"; maps are objects ({"*301": "N"}).
        """
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        unknown = set(raw) - set(cls.__dataclass_fields__)
        if unknown:
            raise ValueError(f"unknown M1 rule(s): {sorted(unknown)}")
        kw: dict[str, Any] = {}
        for k, v in raw.items():
            if k in ("prefixes", "suffixes"):
                kw[k] = tuple(tuple(s.upper() for s in g.split("-")) for g in v)
            elif k == "vowel_signs":
                kw[k] = tuple(s.upper() for s in v)
            elif k in ("special_signs", "initial_class", "interchanges"):
                kw[k] = tuple(sorted((a.upper(), b.upper()) for a, b in v.items()))
            else:
                kw[k] = v
        return cls(**kw)

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("prefixes", "suffixes"):
            d[k] = ["-".join(g) for g in d[k]]
        for k in ("special_signs", "initial_class", "interchanges"):
            d[k] = dict(d[k])
        d["vowel_signs"] = list(d["vowel_signs"])
        return d


class M1(Method):
    """The Finding 001 root matcher behind the benchmark interface."""

    name = "M1"
    layer = "L1"

    def __init__(self, rules: M1Rules | None = None) -> None:
        self.rules = rules or M1Rules()
        r = self.rules
        self._special = dict(r.special_signs)
        self._initial = dict(r.initial_class)
        self._vowels = frozenset(r.vowel_signs)
        self._inter = dict(r.interchanges)
        self._skeletons = lru_cache(maxsize=None)(self._skeletons_uncached)

    # ---- sign side -------------------------------------------------------------------------

    def sign_class(self, sign: str) -> str | None:
        """Consonant class of a sign; None for a pure-vowel sign; "?" if the sign has no usable value."""
        s = sign.upper()
        if s in self._special:
            return self._special[s]
        if s in self._vowels:
            return None
        return self._initial.get(s[0], UNKNOWN)

    def eligible(self, group: SignGroup) -> bool:
        return len(group) >= self.rules.min_group and all(self.sign_class(s) != UNKNOWN for s in group)

    def core_skeletons(self, core: SignGroup) -> Iterator[str]:
        """Candidate consonant skeletons of a core, in the original script's order (duplicates included)."""
        r = self.rules
        signs = [s for i, s in enumerate(core) if i == 0 or s != core[i - 1]] if r.collapse_doubled else list(core)
        slots = [self.sign_class(s) for s in signs]
        if UNKNOWN in slots:
            return
        n_vowels = slots.count(None)
        for choice in itertools.product((0, 1), repeat=n_vowels):
            picks = iter(choice)
            sk = "".join((r.laryngeal if next(picks) else "") if c is None else c for c in slots)
            yield sk
            if len(sk) == 2:  # one unwritten weak radical
                for pos in range(3):
                    for w in r.weak_radicals:
                        yield sk[:pos] + w + sk[pos:]

    def analyses(self, group: SignGroup) -> Iterator[tuple[SignGroup, SignGroup, SignGroup, str]]:
        """Every (prefix, core, suffix, skeleton) the rules allow for a sign-group, in the original order."""
        r = self.rules
        for p in ((),) + r.prefixes:
            if group[:len(p)] != p:
                continue
            for s in ((),) + r.suffixes:
                if s and group[len(group) - len(s):] != s:
                    continue
                core = group[len(p):len(group) - len(s)]
                if not r.min_core <= len(core) <= r.max_core:
                    continue
                for sk in self.core_skeletons(core):
                    if r.min_skeleton <= len(sk) <= r.max_skeleton:
                        yield p, core, s, sk

    def _skeletons_uncached(self, group: SignGroup) -> frozenset[str]:
        return frozenset(a[3] for a in self.analyses(group))

    def skeletons(self, group: SignGroup) -> frozenset[str]:
        """All distinct skeletons a sign-group can be read as. Its size is the group's permissiveness."""
        return self._skeletons(group)

    # ---- lexicon side ----------------------------------------------------------------------

    def variants(self, root: str) -> frozenset[str]:
        """A root with every interchange applied (S as T; D and T either way)."""
        return frozenset("".join(p) for p in itertools.product(*(self._inter.get(c, c) for c in root)))

    def expand(self, form: str) -> frozenset[str]:
        return self.variants(form)

    # ---- matching --------------------------------------------------------------------------

    def match(self, group: SignGroup, prepared: frozenset[str]) -> Match | None:
        if not self.eligible(group):
            return None
        for p, core, s, sk in self.analyses(group):
            if sk in prepared:
                return Match(group, sk, {"prefix": "-".join(p), "core": "-".join(core), "suffix": "-".join(s)})
        return None

    def hits(self, groups: list[SignGroup], prepared: frozenset[str]) -> list[bool]:
        return [self.eligible(g) and not self.skeletons(g).isdisjoint(prepared) for g in groups]

    def degrees_of_freedom(self) -> dict[str, Any]:
        r = self.rules
        classes = sorted({c for c in list(self._initial.values()) + list(self._special.values())} | {r.laryngeal})
        return {
            "sign_value_mergers": {
                "consonant_classes": classes,
                "merged_series": {"K": "k, q", "S": "s, z", "R": "r (Linear B r covers r and l)",
                                  "P": "p (covers p, b, ph)", "T": "t", "D": "d"},
                "lexicon_interchanges": dict(r.interchanges),
            },
            "vowel_signs": {"signs": list(r.vowel_signs), "readings_per_sign": 2,
                            "note": f"each pure-vowel sign is {r.laryngeal} or nothing"},
            "unwritten_radicals": {"applies_to": "two-consonant skeletons", "radicals": r.weak_radicals,
                                   "positions": 3, "extra_readings": 3 * len(r.weak_radicals)},
            "doubled_signs": {"collapse": r.collapse_doubled},
            "affix_menus": {"prefixes": len(r.prefixes), "suffixes": len(r.suffixes),
                            "segmentations_at_most": (len(r.prefixes) + 1) * (len(r.suffixes) + 1)},
            "languages_pooled": {"count": 1, "note": "set by the lexicon passed in, not by the method"},
        }
