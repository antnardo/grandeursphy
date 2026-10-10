import math

import pytest

from grandeurs import constantes, flottants

MODULES = [
    (constantes, flottants),
    (constantes.astro, flottants.astro),
    (constantes.cgs, flottants.cgs),
    (constantes.us, flottants.us),
]


@pytest.mark.parametrize(("grandeurs", "nombres"), MODULES)
def test_memes_noms_que_les_constantes(grandeurs, nombres):
    fonctions = {"FICHES", "Fiche", "codata", "cles_codata", "decrire"}
    assert set(nombres.__all__) == set(grandeurs.__all__) - fonctions


@pytest.mark.parametrize(
    ("grandeurs", "nombres", "nom"),
    [(g, n, nom) for g, n in MODULES for nom in sorted(n.__all__)],
)
def test_flottant_est_la_valeur_si(grandeurs, nombres, nom):
    valeur = getattr(nombres, nom)
    assert type(valeur) is float
    assert valeur == pytest.approx(float(getattr(grandeurs, nom).to_base_units().valeur))


def test_les_quatre_miroirs_couvrent_toutes_les_fiches():
    noms = set()
    for _, nombres in MODULES:
        noms |= set(nombres.__all__)
    assert noms == set(constantes.FICHES)


# Les corrigés existants calculent avec ces flottants : ils doivent être ceux
# que donnait l'ancien paquet constantes quand il était en flottants.
@pytest.mark.parametrize(
    ("nom", "ancien"),
    [
        ("NA", 6.02214076e23),
        ("H", 6.62607015e-34),
        ("HBAR", 6.62607015e-34 / (2 * math.pi)),
        ("E", 1.602176634e-19),
        ("C", 299792458),
        ("R_GP", 1.380649e-23 * 6.02214076e23),
    ],
)
def test_constantes_exactes_identiques_a_l_ancien_calcul(nom, ancien):
    assert getattr(flottants, nom) == ancien


@pytest.mark.parametrize(
    ("nom", "codata_2022"), [("EPS_0", 8.8541878188e-12), ("M_E", 9.1093837139e-31)]
)
def test_constantes_mesurees_en_codata_2022(nom, codata_2022):
    assert getattr(flottants, nom) == codata_2022


def test_calcul_en_flottants_comme_avant():
    assert f"{flottants.R_GP * 1e3:.6e}" == "8.314463e+03"
