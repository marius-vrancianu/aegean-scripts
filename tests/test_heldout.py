from aegean.corpus.heldout import is_heldout, load_heldout


def test_sceptre_is_heldout_in_lineara():
    h = load_heldout()
    for doc in ("KNZg57a", "KNZg57b", "KNZg58"):
        assert is_heldout("lineara.xyz", doc, h)


def test_ordinary_tablet_is_not_heldout():
    assert not is_heldout("lineara.xyz", "HT104")
