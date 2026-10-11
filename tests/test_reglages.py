import warnings

import pytest

from grandeurs import (
    Reglages,
    SansUniteError,
    SansUniteWarning,
    configurer,
    grandeur,
    reglages,
    reglages_temporaires,
)
from grandeurs.reglages import signaler


def test_reglages_par_defaut():
    r = Reglages()
    assert (r.sans_unite, r.chiffres, r.chiffres_significatifs) == ("avertissement", 3, True)


@pytest.mark.parametrize(
    "champs",
    [
        {"sans_unite": "bof"},
        {"decimale": ";"},
        {"chiffres_incertitude": 0},
        {"chiffres": 0},
        {"notation": "sci"},
        {"style_incertitude": "long"},
        {"facteur_elargissement": 0},
        {"facteur_elargissement": -2},
        {"facteur_elargissement": float("inf")},
        {"facteur_elargissement": "2"},
    ],
)
def test_valeur_invalide_refusee(champs):
    with pytest.raises(ValueError):
        Reglages(**champs)


def test_configurer_rend_les_reglages_precedents():
    ancien = configurer(decimale=",")
    try:
        assert reglages().decimale == ","
        assert ancien.decimale == "."
    finally:
        configurer(decimale=ancien.decimale)


def test_reglages_temporaires_restaurent_l_etat():
    avant = reglages()
    with reglages_temporaires(sans_unite="erreur") as r:
        assert r.sans_unite == "erreur"
        assert reglages().sans_unite == "erreur"
    assert reglages() == avant


def test_reglages_temporaires_restaurent_apres_exception():
    avant = reglages()
    with pytest.raises(RuntimeError), reglages_temporaires(notation="fixe"):
        raise RuntimeError
    assert reglages() == avant


def test_signaler_silence_ne_dit_rien():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        signaler("silence", "rien")


def test_signaler_avertissement_emet_sans_unite_warning():
    with pytest.warns(SansUniteWarning, match="oubli"):
        signaler("avertissement", "oubli")


def test_avertissement_designe_la_ligne_de_l_utilisateur():
    with pytest.warns(SansUniteWarning) as releve:
        grandeur(3)
    assert releve[0].filename == __file__


def test_signaler_erreur_leve_sans_unite_error():
    with pytest.raises(SansUniteError, match="oubli"):
        signaler("erreur", "oubli")


def test_facteur_d_elargissement_par_defaut():
    assert Reglages().facteur_elargissement == 2
