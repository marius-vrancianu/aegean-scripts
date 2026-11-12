"""Resampling harness (A1.14), on synthetic witnesses."""
import copy

import pytest

from aegean.corpus import resample


def tok(sign, doubtful=None):
    return {"sign_id": sign, "l1": None, "unidentified": False, "doubtful": doubtful, "components": [], "flags": []}


def wit(doc, source, signs, doubtful=()):
    return {"doc_key": doc, "source": source, "source_id": doc, "lines": [{"items": [
        {"kind": "word", "tokens": [tok(s, True if i in doubtful else False) for i, s in enumerate(signs)]}]}]}


def n_signs(ws):
    return sum(t["sign_id"] is not None for w in ws for ln in w["lines"] for it in ln["items"] for t in it["tokens"])


def n_docs(ws):
    return len(ws)


def corpus():
    ws = [wit("AA 1", "sigla", ["AB001", "AB002"]), wit("AA 1", "lineara.xyz", ["AB001", "AB002", "AB003"]),
          wit("AA 2", "sigla", ["AB004"], doubtful=(0,)), wit("BB 1", "lineara.xyz", ["AB005", "AB006"]),
          wit("BB 2", "lineara.xyz", ["AB007"]), wit("BB 3", "lineara.xyz", ["AB008"] * 10)]
    return resample.group(ws)


def test_group_and_primary_reading():
    c = corpus()
    assert sorted(c) == ["AA 1", "AA 2", "BB 1", "BB 2", "BB 3"] and sorted(c["AA 1"]) == ["lineara.xyz", "sigla"]
    assert n_signs(resample.primary_reading(c, ("sigla", "lineara.xyz"))) == 2 + 1 + 2 + 1 + 10
    assert n_signs(resample.primary_reading(c, ("lineara.xyz", "sigla"))) == 3 + 1 + 2 + 1 + 10
    with pytest.raises(ValueError):
        resample.primary_reading(c, ("younger",))


def test_run_is_reproducible_and_seed_dependent():
    kw = dict(source_order=("sigla", "lineara.xyz"), n=200)
    a, b = resample.run(n_signs, corpus(), seed=3, **kw), resample.run(n_signs, corpus(), seed=3, **kw)
    assert a == b
    assert a["params"]["seed"] == 3 and a["params"]["documents"] == 5 and a["params"]["strata"] == 2
    assert a != resample.run(n_signs, corpus(), seed=4, **kw)


def test_reading_draws_cover_exactly_the_attested_readings():
    r = resample.run(n_signs, corpus(), source_order=("sigla", "lineara.xyz"), seed=1, n=400, p_doubt=0.5)
    # AA 1 has 2 or 3 signs, AA 2 has 1 or 0 (doubtful sign blanked); the rest is fixed at 13.
    assert r["estimate"] == {"value": 16}
    assert (r["reading"]["value"]["min"], r["reading"]["value"]["max"]) == (15, 17)


def test_p_doubt_zero_and_one():
    kw = dict(source_order=("sigla", "lineara.xyz"), seed=1, n=200)
    assert resample.run(n_signs, corpus(), p_doubt=0, **kw)["reading"]["value"]["min"] == 16
    assert resample.run(n_signs, corpus(), p_doubt=1, **kw)["reading"]["value"]["max"] == 16  # 3 + 0 + 13


def test_bootstrap_keeps_stratum_sizes_and_shows_single_document_dependence():
    r = resample.run(n_docs, corpus(), source_order=("sigla", "lineara.xyz"),
                     seed=1, n=200)
    assert r["bootstrap"]["value"]["min"] == r["bootstrap"]["value"]["max"] == 5
    s = resample.run(n_signs, corpus(), source_order=("sigla", "lineara.xyz"), seed=1, n=400)
    # BB 3 holds 10 of the 16 signs: samples without it and samples with it three times both occur.
    assert s["bootstrap"]["value"]["min"] <= 8 and s["bootstrap"]["value"]["max"] >= 30
    assert s["reading"]["value"]["max"] - s["reading"]["value"]["min"] < \
        s["bootstrap"]["value"]["max"] - s["bootstrap"]["value"]["min"]


def test_input_is_never_modified():
    c = corpus()
    before = copy.deepcopy(c)
    resample.run(n_signs, c, source_order=("sigla", "lineara.xyz"), seed=1, n=100, p_doubt=1)
    assert c == before


def test_dict_statistics_and_quantiles():
    r = resample.run(lambda ws: {"signs": n_signs(ws), "docs": n_docs(ws)}, corpus(),
                     source_order=("sigla", "lineara.xyz"), seed=1, n=50)
    assert set(r["estimate"]) == set(r["both"]) == {"signs", "docs"}
    assert resample.quantile([1, 2, 3, 4], 0.5) == 2.5 and resample.quantile([5], 0.975) == 5
    assert r["both"]["signs"]["low"] <= r["both"]["signs"]["median"] <= r["both"]["signs"]["high"]


def test_bad_parameters():
    with pytest.raises(ValueError):
        resample.run(n_signs, {}, source_order=("sigla",), seed=1)
    with pytest.raises(ValueError):
        resample.run(n_signs, corpus(), source_order=("sigla", "lineara.xyz"), seed=1, p_doubt=2)
