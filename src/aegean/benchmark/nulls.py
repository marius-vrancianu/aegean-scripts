"""Null models for the benchmark (CLAUDE.md rule 1; docs/guardrails.md items 1 and 2).

Three nulls, each answering a different question:

1. **Matched pseudo-lexicons** (`matched_lexicon`). A lexicon of no language
   that the method sees as the same size as the real one: the same number of
   distinct forms *after the method's own lexicon-side licences* (`expand`),
   lengths drawn from the real lexicon, and letters drawn with the real
   lexicon's frequencies for that length and position. Question: does the
   real lexicon fit the sign-groups better than a lexicon of no language?
   This is the null the Tier 1 decision uses.
1a. **Length-stratified matched pseudo-lexicons** (`stratified_matched_lexicon`;
   the decision null of protocol H-A5-03). As (1), but filled length by
   length: at each form length the pseudo-lexicon has exactly the real
   lexicon's number of distinct forms *after expansion*. Null (1) draws a
   length per form and redraws repeats; short forms repeat more often, so it
   ends with fewer short forms than the real lexicon (H-A5-02 outcome). This
   null removes that bias by construction.
1c. **Bigram-matched, length-stratified pseudo-lexicons** (`bigram_matched_lexicon`;
   candidate decision null of a second protocol revision). As (1a), but letters
   are drawn from a first-order Markov chain fitted to the real lexicon: the
   first letter from the real first-letter frequencies at that length, every
   later letter from the real frequencies of what follows the previous letter
   (pooled over all lengths and positions). This matches adjacent-letter
   co-occurrence, which (1a) does not.
1d. **Position-aware bigram-matched, length-stratified pseudo-lexicons**
   (`positional_bigram_matched_lexicon`; the decision null of protocol H-A5-09).
   As (1c), but every transition is conditioned on the form's length and the
   position: letter i is drawn from the real frequencies of what follows the
   previous letter at that length and position. So it keeps (1a)'s per-position
   letter frequencies and adds adjacent-letter co-occurrence. The price: it
   reproduces more of the real lexicon's own forms (H-A5-09).
1b. **Finding 001 pseudo-lexicons** (`pseudo_lexicon`). The same number of
   forms *before* the method's licences and overall letter frequencies only.
   Kept because Finding 001 used it. It is not size-matched as the method
   sees it: for M1 and the Hebrew verbs the real lexicon expands to 664
   forms, these to about 743, so this null matches more often than a
   fair one would (research-notes 2026-11-14, A5.17).
2. **Random sign strings** (`random_sign_strings`). Strings with the lengths
   of the real sign-groups and the corpus's sign frequencies. Question: do
   real sign-groups differ from random strings under this method? They can
   differ for reasons that have nothing to do with the lexicon (repeated
   endings that the method's affix menus strip), so this null is reported but
   decides nothing about a language.

Synthetic text made here is a null corpus only (CLAUDE.md rule 9): it is
never written into the corpus and never counts as evidence.

Every function takes a `random.Random`. `pseudo_lexicon` draws exactly as
Finding 001's run2.py did, so `random.Random(7)` reproduces that run's 20
lexicons one after the other.
"""
from __future__ import annotations

import collections
import random

from aegean.benchmark.interface import Lexicon, Method, SignGroup


def letter_frequencies(forms: list[str]) -> tuple[list[str], list[int]]:
    """Letters in order of first appearance in `forms`, and their counts."""
    freq = collections.Counter(c for f in forms for c in f)
    letters = list(freq)
    return letters, [freq[c] for c in letters]


def pseudo_lexicon(real: Lexicon, rng: random.Random, size_factor: float = 1.0, index: int | None = None) -> Lexicon:
    """A random lexicon with int(size_factor * len(real)) distinct forms.

    Each form takes the length of a real form drawn at random, and letters drawn with the real lexicon's
    letter frequencies. Duplicates are redrawn, so the size is exact. `index` only labels the result.
    """
    base = sorted(real.forms)
    letters, weights = letter_frequencies(base)
    target = int(len(base) * size_factor)
    if target < 1:
        raise ValueError("size_factor too small: the pseudo-lexicon would be empty")
    capacity = sum(len(letters) ** n for n in {len(b) for b in base})
    if target > capacity:
        raise ValueError(f"cannot draw {target} distinct forms: only {capacity} exist at these lengths")
    fake: set[str] = set()
    while len(fake) < target:
        fake.add("".join(rng.choices(letters, weights, k=len(rng.choice(base)))))
    label = f"null({real.name})" + (f"x{size_factor:g}" if size_factor != 1 else "") + (f"#{index}" if index is not None else "")
    return Lexicon(label, frozenset(fake), "null", {"of": real.name, "size_factor": size_factor, "index": index})


def positional_frequencies(forms: list[str]) -> dict[int, list[tuple[list[str], list[int]]]]:
    """For each form length, and each position in it: the letters seen there (sorted) and their counts."""
    counts: dict[int, list[collections.Counter]] = {}
    for f in forms:
        cs = counts.setdefault(len(f), [collections.Counter() for _ in f])
        for i, c in enumerate(f):
            cs[i][c] += 1
    return {n: [(sorted(c), [c[x] for x in sorted(c)]) for c in cs] for n, cs in counts.items()}


def matched_lexicon(real: Lexicon, method: Method, rng: random.Random, index: int | None = None,
                    max_draws: int = 1_000_000) -> Lexicon:
    """A random lexicon that `method` sees as exactly as large as `real`.

    Forms are drawn one at a time: the length of a real form drawn at random, then each letter from the real
    lexicon's frequencies at that length and position. A form is kept unless it is a duplicate or would take
    the number of distinct expanded forms past the real lexicon's; drawing stops when the two are equal.
    """
    base = sorted(real.forms)
    target = len(method.prepare(real))
    freqs = positional_frequencies(base)
    fake: set[str] = set()
    expanded: set[str] = set()
    for _ in range(max_draws):
        if len(expanded) == target:
            break
        form = "".join(rng.choices(letters, weights)[0] for letters, weights in freqs[len(rng.choice(base))])
        if form in fake:
            continue
        new = method.expand(form) - expanded
        if len(expanded) + len(new) > target:
            continue
        fake.add(form)
        expanded |= new
    else:
        raise RuntimeError(f"no matched lexicon after {max_draws} draws ({len(expanded)} of {target} expanded forms)")
    label = f"matched({real.name})" + (f"#{index}" if index is not None else "")
    return Lexicon(label, frozenset(fake), "null", {"of": real.name, "index": index, "expanded_forms": target})


def stratified_matched_lexicon(real: Lexicon, method: Method, rng: random.Random, index: int | None = None,
                               max_draws: int = 1_000_000) -> Lexicon:
    """A random lexicon with, at every form length, exactly as many expanded forms as `real` has.

    Lengths are taken in increasing order. At each length, forms are drawn letter by letter from the real
    lexicon's frequencies at that length and position; a form is kept unless it is a duplicate or would take
    the number of distinct expanded forms of that length past the real lexicon's. (The method's expansion must
    keep lengths, as M1's letter interchanges do; anything else is an error.)
    """
    base = sorted(real.forms)
    freqs = positional_frequencies(base)
    target: dict[int, int] = {}
    for f in method.prepare(real):
        target[len(f)] = target.get(len(f), 0) + 1
    if set(target) != set(freqs):
        raise ValueError("the method's expansion changes form lengths; a length-stratified null is not defined")
    fake: set[str] = set()
    draws = 0
    for n in sorted(target):
        expanded: set[str] = set()
        while len(expanded) < target[n]:
            draws += 1
            if draws > max_draws:
                raise RuntimeError(f"no stratified lexicon after {max_draws} draws (length {n}: "
                                   f"{len(expanded)} of {target[n]} expanded forms)")
            form = "".join(rng.choices(letters, weights)[0] for letters, weights in freqs[n])
            if form in fake:
                continue
            new = method.expand(form)
            if any(len(x) != n for x in new):
                raise ValueError(f"expansion of {form!r} changes its length")
            new = new - expanded
            if len(expanded) + len(new) > target[n]:
                continue
            fake.add(form)
            expanded |= new
    label = f"stratified({real.name})" + (f"#{index}" if index is not None else "")
    return Lexicon(label, frozenset(fake), "null", {"of": real.name, "index": index,
                                                    "expanded_forms_by_length": dict(sorted(target.items()))})


def bigram_model(forms: list[str]) -> tuple[dict[int, tuple[list[str], list[int]]], dict[str, tuple[list[str], list[int]]]]:
    """(first-letter frequencies per length, next-letter frequencies per letter) of a list of forms."""
    first: dict[int, collections.Counter] = {}
    nxt: dict[str, collections.Counter] = {}
    for f in forms:
        first.setdefault(len(f), collections.Counter())[f[0]] += 1
        for a, b in zip(f, f[1:]):
            nxt.setdefault(a, collections.Counter())[b] += 1
    pack = lambda c: (sorted(c), [c[x] for x in sorted(c)])
    return {n: pack(c) for n, c in first.items()}, {a: pack(c) for a, c in nxt.items()}


def bigram_matched_lexicon(real: Lexicon, method: Method, rng: random.Random, index: int | None = None,
                           max_draws: int = 1_000_000) -> Lexicon:
    """A random lexicon with the real lexicon's expanded-form count at every length and its letter transitions.

    As `stratified_matched_lexicon`, except that a form is drawn from a first-order Markov chain fitted to the
    real lexicon's forms (`bigram_model`). A letter that is never followed by anything in the real lexicon
    (it occurs only finally) ends the draw early; such a draw is discarded and redrawn.
    """
    base = sorted(real.forms)
    first, nxt = bigram_model(base)
    target: dict[int, int] = {}
    for f in method.prepare(real):
        target[len(f)] = target.get(len(f), 0) + 1
    if set(target) != set(first):
        raise ValueError("the method's expansion changes form lengths; a length-stratified null is not defined")
    fake: set[str] = set()
    draws = 0
    for n in sorted(target):
        expanded: set[str] = set()
        while len(expanded) < target[n]:
            draws += 1
            if draws > max_draws:
                raise RuntimeError(f"no bigram lexicon after {max_draws} draws (length {n}: "
                                   f"{len(expanded)} of {target[n]} expanded forms)")
            letters, weights = first[n]
            form = rng.choices(letters, weights)[0]
            while len(form) < n and form[-1] in nxt:
                letters, weights = nxt[form[-1]]
                form += rng.choices(letters, weights)[0]
            if len(form) < n or form in fake:
                continue
            new = method.expand(form)
            if any(len(x) != n for x in new):
                raise ValueError(f"expansion of {form!r} changes its length")
            new = new - expanded
            if len(expanded) + len(new) > target[n]:
                continue
            fake.add(form)
            expanded |= new
    label = f"bigram({real.name})" + (f"#{index}" if index is not None else "")
    return Lexicon(label, frozenset(fake), "null", {"of": real.name, "index": index,
                                                    "expanded_forms_by_length": dict(sorted(target.items()))})


def positional_bigram_model(forms: list[str]) -> tuple[dict, dict]:
    """(first-letter frequencies per length, next-letter frequencies per (length, position, previous letter))."""
    first: dict[int, collections.Counter] = {}
    trans: dict[tuple[int, int, str], collections.Counter] = {}
    for f in forms:
        first.setdefault(len(f), collections.Counter())[f[0]] += 1
        for i in range(1, len(f)):
            trans.setdefault((len(f), i, f[i - 1]), collections.Counter())[f[i]] += 1
    pack = lambda c: (sorted(c), [c[x] for x in sorted(c)])
    return {n: pack(c) for n, c in first.items()}, {k: pack(c) for k, c in trans.items()}


def positional_bigram_matched_lexicon(real: Lexicon, method: Method, rng: random.Random, index: int | None = None,
                                      max_draws: int = 1_000_000) -> Lexicon:
    """A random lexicon with the real lexicon's expanded-form count at every length, its per-position letters,
    and its letter transitions at each length and position (`positional_bigram_model`).

    Every transition used has been seen in the real lexicon at the same length and position, so a draw can never
    get stuck; a draw that cannot continue is impossible by construction but would be discarded and redrawn.
    """
    base = sorted(real.forms)
    first, trans = positional_bigram_model(base)
    target: dict[int, int] = {}
    for f in method.prepare(real):
        target[len(f)] = target.get(len(f), 0) + 1
    if set(target) != set(first):
        raise ValueError("the method's expansion changes form lengths; a length-stratified null is not defined")
    fake: set[str] = set()
    draws = 0
    for n in sorted(target):
        expanded: set[str] = set()
        while len(expanded) < target[n]:
            draws += 1
            if draws > max_draws:
                raise RuntimeError(f"no positional bigram lexicon after {max_draws} draws (length {n}: "
                                   f"{len(expanded)} of {target[n]} expanded forms)")
            letters, weights = first[n]
            form = rng.choices(letters, weights)[0]
            for i in range(1, n):
                t = trans.get((n, i, form[-1]))
                if t is None:
                    break
                form += rng.choices(t[0], t[1])[0]
            if len(form) < n or form in fake:
                continue
            new = method.expand(form)
            if any(len(x) != n for x in new):
                raise ValueError(f"expansion of {form!r} changes its length")
            new = new - expanded
            if len(expanded) + len(new) > target[n]:
                continue
            fake.add(form)
            expanded |= new
    label = f"posbigram({real.name})" + (f"#{index}" if index is not None else "")
    return Lexicon(label, frozenset(fake), "null", {"of": real.name, "index": index,
                                                    "expanded_forms_by_length": dict(sorted(target.items()))})


def random_sign_strings(lengths: list[int], sign_pool: list[str], rng: random.Random) -> list[SignGroup]:
    """One random sign string per entry of `lengths`, each sign drawn from `sign_pool` (with its frequencies)."""
    if not sign_pool:
        raise ValueError("empty sign pool")
    return [tuple(rng.choice(sign_pool) for _ in range(n)) for n in lengths]
