import numpy as np
import pytest
from uncertainties import UFloat, ufloat

from grandeurs import NombreArrondi, arrondir, lire_nombre, reglages_temporaires
from grandeurs.chiffres import arrondir_valeur


@pytest.mark.parametrize(
    ("texte", "valeur", "incertitude", "reste"),
    [
        ("1.20 m.s-1", 1.20, 0.01, "m.s-1"),
        ("1200", 1200, 1, ""),
        ("1.2e3 m", 1200, 100, "m"),
        ("1.20(3) m", 1.20, 0.03, "m"),
        ("1.20(3)e3 m", 1200, 30, "m"),
        ("1.20 ± 0.03 m", 1.20, 0.03, "m"),
        ("1.20+/-0.03", 1.20, 0.03, ""),
        ("(1.20 ± 0.03)e3 m", 1200, 30, "m"),
        ("1.20e3 ± 30 g", 1200, 30, "g"),
        ("1,20 m", 1.20, 0.01, "m"),
        ("1.20×10^3 m", 1200, 10, "m"),
        ("1.20 × 10⁻³ m", 1.20e-3, 1e-5, "m"),
        ("1.20x10^{-3}", 1.20e-3, 1e-5, ""),
        ("1.20×10³ m", 1200, 10, "m"),
        ("-0.5 K", -0.5, 0.1, "K"),
        ("12 g.mol-1", 12, 1, "g.mol-1"),
    ],
)
def test_lire_nombre_donne_valeur_incertitude_et_unite(texte, valeur, incertitude, reste):
    lu, suite = lire_nombre(texte)
    assert lu.nominal_value == pytest.approx(valeur)
    assert lu.std_dev == pytest.approx(incertitude)
    assert suite == reste


def test_lire_nombre_sans_chiffres_significatifs_donne_un_flottant_exact():
    lu, _ = lire_nombre("1.20 m", chiffres_significatifs=False)
    assert not isinstance(lu, UFloat)
    assert lu == 1.2


def test_lire_nombre_illisible_leve_value_error():
    with pytest.raises(ValueError, match="aucun nombre"):
        lire_nombre("m.s-1")


@pytest.mark.parametrize(
    ("valeur", "incertitude", "attendu"),
    [
        (1.2, 0.01, "1.20(1)"),
        (1.2345, 0.0096, "1.23(1)"),
        (-1.2345, 0.0096, "-1.23(1)"),
        (1234.5, 12, "1.23(1)e3"),
        (0.000123, 0.000004, "1.23(4)e-4"),
        (12345.678, 0.5, "12345.7(5)"),
        (0.0, 0.02, "0.00(2)"),
    ],
)
def test_arrondir_au_rang_de_l_incertitude(valeur, incertitude, attendu):
    assert arrondir(valeur, incertitude).ecrire() == attendu


def test_arrondir_deux_chiffres_sur_l_incertitude():
    assert arrondir(1234.5, 12, chiffres_incertitude=2).ecrire() == "1235(12)"


@pytest.mark.parametrize(
    ("valeur", "chiffres", "attendu"),
    [(2.675, 3, "2.68"), (9.96, 2, "10"), (8314.46261815324, 4, "8314"), (0.0, 3, "0.00")],
)
def test_arrondir_a_n_chiffres_significatifs_au_plus_proche(valeur, chiffres, attendu):
    assert arrondir(valeur, chiffres=chiffres).ecrire() == attendu


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        (299792458.0, "2.99792458e8"),
        (6.02214076e23, "6.02214076e23"),
        (1200.0, "1200"),
        (0.1 + 0.2, "0.3"),
        (999.9999999999999, "1000"),
        (1e-7, "1e-7"),
    ],
)
def test_valeur_exacte_ecrite_sans_bruit_de_conversion(valeur, attendu):
    assert arrondir(valeur).ecrire() == attendu


def test_nombre_arrondi_porte_ses_chiffres_significatifs():
    assert arrondir(1.2, 0.01) == NombreArrondi(False, "120", -2, 1)
    assert arrondir(1.2, 0.01).nombre_chiffres == 3


@pytest.mark.parametrize(
    ("options", "attendu"),
    [
        ({"incertitude": "pm"}, "(1.23 ± 0.01)e3"),
        ({"incertitude": None}, "1.23e3"),
        ({"notation": "fixe"}, "1230(10)"),
        ({"notation": "ingenieur"}, "1.23(1)e3"),
        ({"decimale": ","}, "1,23(1)e3"),
    ],
)
def test_ecrire_selon_les_options(options, attendu):
    assert arrondir(1234.5, 12).ecrire(**options) == attendu


def test_ecrire_ingenieur_met_l_exposant_multiple_de_trois():
    assert arrondir(0.000123, 0.000004).ecrire(notation="ingenieur") == "123(4)e-6"


def test_valeur_non_finie_ecrite_telle_quelle():
    assert arrondir(float("-inf")).ecrire() == "-inf"


class TestArrondirValeur:
    def test_valeur_exacte_au_reglage_chiffres(self):
        assert arrondir_valeur(9.79828445167129).ecrire() == "9.80"
        with reglages_temporaires(chiffres=5):
            assert arrondir_valeur(9.79828445167129).ecrire() == "9.7983"

    def test_valeur_incertaine_arrondie_d_apres_l_incertitude(self):
        assert arrondir_valeur(ufloat(9.79828, 0.02)).ecrire() == "9.80(2)"
        with reglages_temporaires(chiffres=5):
            assert arrondir_valeur(ufloat(9.79828, 0.02)).ecrire() == "9.80(2)"

    def test_chiffres_explicite_masque_l_incertitude(self):
        assert arrondir_valeur(ufloat(9.79828, 0.02), chiffres=2).ecrire() == "9.8"

    def test_nombre_numpy_accepte(self):
        assert arrondir_valeur(np.float64(2.0)).ecrire() == "2.00"
