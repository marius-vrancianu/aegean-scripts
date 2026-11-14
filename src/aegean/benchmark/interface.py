"""The common interface of the benchmark (plan §0.7, A5.17 step 1).

A *method* takes a sign-group and a lexicon and returns a match or nothing.

- A **sign-group** is a tuple of L1 values, upper case: ("JA", "DI", "KI", "TU").
  Signs without a conventional value are "*" + number ("*301").
- A **lexicon** is a set of forms in the alphabet the method compares against
  (for M1: consonant-class skeletons such as "KTR"). How a language's
  dictionary becomes such forms is part of the claim under test and is done by
  a loader in `aegean.benchmark.lexicons`, never by the runner.
- A **match** says which lexicon form was reached and by which analysis.

A method must be a pure function of (sign-group, lexicon): no state carried
from one sign-group to the next, no access to the corpus, no randomness. The
runner relies on this to cache per-group work across many null lexicons.

To add a method (M2 ...): subclass `Method`, give it a `name`, and implement
`eligible`, `match` and `degrees_of_freedom` (and `expand` if
its licences widen the lexicon). Plan §0.7 step 5:
no method beyond M1 is added before the protocol (A5.13) is merged.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

SignGroup = tuple[str, ...]

# The six ways a method widens its hit rate (docs/guardrails.md, item 3). Every method reports each one.
DOF_ITEMS = (
    "sign_value_mergers",
    "vowel_signs",
    "unwritten_radicals",
    "doubled_signs",
    "affix_menus",
    "languages_pooled",
)


@dataclass(frozen=True)
class Lexicon:
    """A named set of comparison forms. `kind` is "real" or "null"; `meta` records how it was made."""
    name: str
    forms: frozenset[str]
    kind: str = "real"
    meta: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)

    def __post_init__(self) -> None:
        if self.kind not in ("real", "null"):
            raise ValueError(f"kind must be 'real' or 'null', got {self.kind!r}")
        if not self.forms:
            raise ValueError(f"lexicon {self.name!r} is empty")

    def __len__(self) -> int:
        return len(self.forms)


@dataclass(frozen=True)
class Match:
    """One sign-group matched to one lexicon form. `analysis` is the method's own account of how."""
    sign_group: SignGroup
    form: str
    analysis: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)


class Method(ABC):
    """A lexical-matching method under test."""

    name: str = ""
    layer: str = "L1"

    @abstractmethod
    def eligible(self, group: SignGroup) -> bool:
        """Whether the method can be applied to this sign-group at all (length, known sign values).

        Hit rates are computed over eligible groups only; the runner reports how many were not eligible.
        """

    def expand(self, form: str) -> frozenset[str]:
        """Every comparison form that one lexicon form stands for under the method's lexicon-side licences.

        The default is the form itself. The size of a lexicon *as the method sees it* is the number of
        distinct forms after this expansion; the matched null (`aegean.benchmark.nulls`) equalises it.
        """
        return frozenset((form,))

    def prepare(self, lexicon: Lexicon) -> Any:
        """Whatever the method derives from a lexicon once. Default: the union of `expand` over its forms.

        A method that overrides this must keep `expand` consistent with it.
        """
        out: set[str] = set()
        for form in lexicon.forms:
            out |= self.expand(form)
        return frozenset(out)

    @abstractmethod
    def match(self, group: SignGroup, prepared: Any) -> Match | None:
        """The method's match for one sign-group against one prepared lexicon, or None."""

    @abstractmethod
    def degrees_of_freedom(self) -> dict[str, Any]:
        """The method's licences under each item of `DOF_ITEMS` (docs/guardrails.md, item 3)."""

    def hits(self, groups: list[SignGroup], prepared: Any) -> list[bool]:
        """Whether each sign-group matches. Methods may override this with something faster."""
        return [self.match(g, prepared) is not None for g in groups]


def normalise(group) -> SignGroup:
    """A sign-group as a tuple of upper-case values. Accepts "ja-di-ki-tu" or a sequence of values."""
    parts = group.split("-") if isinstance(group, str) else group
    out = tuple(str(p).strip().upper() for p in parts)
    if not out or any(not p for p in out):
        raise ValueError(f"empty sign or sign-group: {group!r}")
    return out
