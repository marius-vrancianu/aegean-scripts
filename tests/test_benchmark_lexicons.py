"""Lexicon loaders of the benchmark (A5.17). Expected values hand-checked against the sources named in each test."""
import pytest

from aegean.benchmark import lexicons as L

# index.verb lines in WordNet 3.0 format (wndb(5)): lemma pos synset_cnt p_cnt [ptrs] sense_cnt tagsense_cnt offsets.
# Counts made up; the field layout is that of the real `make` line ("make v 49 8 ! @ ~ * ^ $ + ; 49 29 ...").
INDEX = "\n".join([
    "  1 This software and database is being provided to you",  # licence header lines start with spaces
    "make v 2 3 ! @ ~ 2 29 02560585 00120316",
    "take v 1 1 @ 1 36 01212345",
    "go v 1 1 @ 1 40 01234567",            # one consonant: too short
    "look_up v 1 1 @ 1 50 01111111",       # two words: skipped
    "strengthen v 1 1 @ 1 5 02222222",      # five consonants: too long
    "abet v 1 1 @ 1 3 03333333",
    "abate v 1 1 @ 1 3 04444444",           # same skeleton as abet: duplicate
    "zzyzx v 1 1 @ 1 1 05555555",           # no pronunciation
])
# CMUdict lines (format of cmudict.dict at the pinned commit); stress digits are removed by the loader.
CMU = "\n".join([
    "make M EY1 K", "make(2) M EY1 K S", "take T EY1 K", "go G OW1",
    "strengthen S T R EH1 NG K TH AH0 N", "abet AH0 B EH1 T", "abate AH0 B EY1 T",
    "church CH ER1 CH # comment",
])


def test_cmudict_first_pronunciation_without_stress():
    p = L.cmudict_first(CMU)
    assert p["make"] == ["M", "EY", "K"] and p["church"] == ["CH", "ER", "CH"]


@pytest.mark.parametrize("phones, want", [
    (["M", "EY", "K"], "MK"),                 # make
    (["TH", "IH", "NG", "K"], "TNK"),         # think: th -> T, ng -> N
    (["B", "R", "IH", "NG"], "PRN"),          # bring
    (["JH", "AH", "JH"], "SS"),               # judge: affricates are sibilants
    (["W", "ER", "IY"], "WR"),                # worry: r-coloured vowel -> R
    (["HH", "AE", "V"], "HP"),                # have: h -> H, v -> P
    (["DH", "IH", "S"], "DS"),                # 'this' (not a verb; shows dh -> D)
    (["Y", "EH", "L"], "JR"),                 # yell
])
def test_english_skeleton(phones, want):
    assert L.english_skeleton(phones) == want


def test_wordnet_verbs_and_ranking():
    verbs = dict(L.wordnet_verbs(INDEX))
    assert verbs["make"] == 29 and verbs["take"] == 36 and "look_up" not in verbs
    forms, info = L.english_verb_skeletons(INDEX, CMU, size=3)
    # Ranked: look_up excluded; go 40 (too short), take 36, make 29, strengthen 5 (too long), then the ties at 3
    # alphabetically: abate is taken, and the loop stops at three forms before abet is reached.
    assert forms == {"TK", "MK", "PT"}
    assert info["skipped"] == {"no_pronunciation": 0, "length": 2, "duplicate": 0}
    assert info["last_verb_taken"] == ("abate", 3)
    with pytest.raises(ValueError, match="only 3 distinct"):  # abet duplicates abate; zzyzx has no pronunciation
        L.english_verb_skeletons(INDEX, CMU, size=4)
    _, info = L.english_verb_skeletons(INDEX, CMU + "\nzzyzx Z IH1 Z IH0 K S", size=4)
    assert info["skipped"] == {"no_pronunciation": 0, "length": 2, "duplicate": 1}


needs_english = pytest.mark.skipif(not (L.CMUDICT.exists() and L.WORDNET_ZIP.exists()),
                                   reason="run data/raw/cmudict/fetch.py and data/raw/wordnet/fetch.py")


@needs_english
def test_english_verbs_lexicon():
    lex = L.english_verbs()
    assert len(lex) == 502 and lex.meta["verbs_ranked"] == 8429 and lex.meta["last_verb_taken"] == ("hurtle", 2)
    # the most frequent verbs, converted by hand from their CMUdict entries
    assert {"TK", "MK", "RN", "KP", "HRD", "PRK", "PR", "DR", "KT", "KS", "HP", "PS", "KR"} <= lex.forms
    assert {len(f) for f in lex.forms} == {2, 3, 4}
