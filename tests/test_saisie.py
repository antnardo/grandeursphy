import numpy as np
import pint
import pytest

from grandeurs import (
    Grandeur,
    SansUniteError,
    SansUniteWarning,
    grandeur,
    reglages_temporaires,
    unit,
    ureg,
)


@pytest.mark.parametrize(
    ("texte", "nom"),
    [
        ("m.s-1", "meter / second"),
        ("m·s⁻¹", "meter / second"),
        ("kg.m.s^(-2)", "kilogram * meter / second ** 2"),
        ("mol.L-1", "mole / liter"),
        ("J.mol-1.K-1", "joule / mole / kelvin"),
        ("µm", "micrometer"),
        ("°C", "degree_Celsius"),
        ("mL", "milliliter"),
        ("Ω", "ohm"),
    ],
)
def test_unit_lit_les_notations_de_manuel(texte, nom):
    assert unit(texte).pint_unit == ureg.parse_units(nom)


def test_unit_accepte_unite_pint_et_grandeur():
    assert unit(pint.get_application_registry().get().Unit("m")) == "m"
    assert unit(grandeur(3, "m/s")) == "m.s-1"
    assert unit(unit("m")) == "m"


def test_unit_refuse_un_nombre():
    with pytest.raises(TypeError):
        unit(3)


def test_grandeur_depuis_une_chaine():
    g = grandeur("1.20 m.s-1")
    assert isinstance(g, Grandeur)
    assert g.unite == unit("m/s")


def test_grandeur_depuis_une_chaine_et_une_unite():
    assert grandeur("1.20", "m").unite == unit("m")


def test_grandeur_convertie_si_la_chaine_a_deja_une_unite():
    assert grandeur("1.20 km", "m").valeur == pytest.approx(1200)


def test_grandeur_convertie_depuis_une_grandeur():
    assert grandeur(grandeur(1, "km"), "m").valeur == 1000


def test_grandeur_d_un_autre_registre():
    autre = pint.UnitRegistry()
    assert grandeur(autre.Quantity(2, "km")).unite == unit("km")


def test_incertitude_absolue():
    g = grandeur(1.2, "m", incertitude=0.05)
    assert g.incertitude == 0.05


def test_incertitude_avec_unite():
    assert grandeur(1.2, "m", incertitude="5 cm").incertitude == pytest.approx(0.05)


def test_incertitude_sur_un_tableau():
    g = grandeur(np.array([1.0, 2.0]), "m", incertitude=0.1)
    assert list(g.incertitude) == [0.1, 0.1]


def test_double_incertitude_refusee():
    with pytest.raises(ValueError, match="déjà"):
        grandeur("1.20 m", incertitude=0.1)


def test_sans_unite_avertit_et_donne_une_grandeur_sans_dimension():
    with pytest.warns(SansUniteWarning, match="sans unité"):
        g = grandeur(3)
    assert g.dimensionless


def test_sans_dimension_explicite_ne_dit_rien():
    assert grandeur(0.5, "").dimensionless
    assert grandeur(0.5, "1").dimensionless


def test_sans_unite_en_silence(silence):
    assert grandeur(3).valeur == 3


def test_sans_unite_refusee_au_niveau_erreur():
    with reglages_temporaires(sans_unite="erreur"), pytest.raises(SansUniteError):
        grandeur("3.0")


class TestFormeNommee:
    def test_u_est_l_incertitude_type(self):
        g = grandeur("x = 1.20 m ; u(x) = 0.04 m")
        assert (g.valeur, g.incertitude, g.unite) == (1.2, pytest.approx(0.04), unit("m"))

    def test_grand_u_est_l_incertitude_elargie(self):
        assert grandeur("x = 1.20 m ; U(x) = 0.04 m").incertitude == pytest.approx(0.02)
        with reglages_temporaires(facteur_elargissement=4):
            assert grandeur("x = 1.20 m ; U(x) = 0.04 m").incertitude == pytest.approx(0.01)

    def test_convertit_l_incertitude_dans_l_unite_de_la_valeur(self):
        assert grandeur("L = 1.20 m ; u(L) = 4 cm").incertitude == pytest.approx(0.04)

    def test_convertie_dans_l_unite_demandee(self):
        g = grandeur("x = 1.20 m ; U(x) = 0.04 m", "cm")
        assert (g.valeur, g.incertitude) == pytest.approx((120, 2))

    def test_sans_unite_avertit(self):
        with pytest.warns(SansUniteWarning):
            g = grandeur("x = 0.500 ; u(x) = 0.002")
        assert g.incertitude == pytest.approx(0.002)

    def test_valeur_deja_incertaine_refusee(self):
        with pytest.raises(ValueError, match="déjà"):
            grandeur("x = 1.20 ± 0.02 m ; u(x) = 0.04 m")


def test_chaines_exactes_si_reglage():
    with reglages_temporaires(chiffres_significatifs=False):
        assert grandeur("1.20 m").incertitude == 0.0
