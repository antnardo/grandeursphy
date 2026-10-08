import math

import pytest

from grandeurs import constantes, flottants


def test_memes_noms_que_les_constantes():
    assert set(flottants.__all__) == set(constantes.FICHES)


@pytest.mark.parametrize("nom", sorted(constantes.FICHES))
def test_flottant_est_la_valeur_si(nom):
    valeur = getattr(flottants, nom)
    assert type(valeur) is float
    assert valeur == pytest.approx(float(getattr(constantes, nom).to_base_units().valeur))


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
