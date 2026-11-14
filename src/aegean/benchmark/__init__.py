"""A5: benchmark of lexical-matching ("Linear A is language X") methods.

Tier 1 (A5.17): false-positive rates. How often does a method "find" a
language that is not there? Design: plan §0.7; protocol: hypotheses/H-A5-01.md.

Layer: L1. A lexical-matching method reads sign-groups as conventional
Linear B values, so every result here is conditional on those values holding
for Linear A (untested: plan A4).

Modules
- interface   the common Method interface, Lexicon and Match
- m1          method M1: the Finding 001 ("Ya Diktu") root matcher
- lexicons    real lexicons (Hebrew verb skeletons from Strong's)
- nulls       random pseudo-lexicons and random sign strings
- inputs      Linear A sign-groups (via aegean.corpus.load) and the Linear B control words
- tier1       the Tier 1 runner and command line
"""
