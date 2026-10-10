import numpy as np
import pytest
from pint import DimensionalityError
from uncertainties import UFloat

from grandeurs import Grandeur, grandeur, reglages_temporaires, unit


class TestValeurEtIncertitude:
    def test_chaine_porte_ses_chiffres_significatifs(self):
        v = grandeur("1.20 m.s-1")
        assert (v.valeur, v.incertitude, v.chiffres) == (1.2, 0.01, 3)

    def test_valeur_exacte_sans_incertitude(self):
        g = grandeur(1.2, "m")
        assert g.incertitude == 0.0
        assert g.chiffres is None

    def test_incertitude_relative(self):
        assert grandeur("2.00 m").incertitude_relative == pytest.approx(0.005)

    def test_valeur_si_pour_revenir_aux_flottants(self):
        assert grandeur(20, "°C").valeur_si == pytest.approx(293.15)
        assert grandeur(36, "km/h").valeur_si == pytest.approx(10)

    def test_tableau_d_incertitudes(self):
        g = grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.2])
        assert list(g.valeur) == [1.0, 2.0]
        assert list(g.incertitude) == [0.1, 0.2]
        assert list((2 * g).incertitude) == pytest.approx([0.2, 0.4])


class TestPropagation:
    def test_produit_propage_les_incertitudes_relatives(self):
        d = grandeur("1.20 m.s-1") * grandeur("2.0 s")
        assert d.valeur == pytest.approx(2.4)
        assert d.incertitude == pytest.approx(2.4 * np.hypot(0.01 / 1.2, 0.1 / 2.0))
        assert d.unite == unit("m")

    def test_correlation_a_moins_a_vaut_zero(self):
        a = grandeur("1.20 m")
        assert (a - a).incertitude == 0.0
        assert (a / a).incertitude == 0.0

    def test_somme_convertit_les_unites(self):
        s = grandeur("1.20 m") + grandeur("3.0 cm")
        assert s.valeur == pytest.approx(1.23)
        assert s.incertitude == pytest.approx(np.hypot(0.01, 0.001))

    def test_resultat_reste_une_grandeur(self):
        assert isinstance(grandeur("1.20 m") * 2, Grandeur)
        assert isinstance(np.sqrt(grandeur(4.0, "m2")), Grandeur)


class TestOperationsDeprecieesParUncertainties:
    def test_valeur_absolue_garde_l_incertitude(self):
        a = grandeur("-1.20 m")
        assert (abs(a).valeur, abs(a).incertitude) == (1.2, 0.01)
        assert (abs(a) + a).incertitude == 0.0  # corrélation conservée

    def test_valeur_absolue_d_un_tableau(self):
        g = abs(grandeur([-1.0, 2.0], "m", incertitude=0.1))
        assert list(g.valeur) == [1.0, 2.0]

    def test_arrondir_une_grandeur_incertaine_refuse(self):
        with pytest.raises(TypeError, match="chiffres"):
            round(grandeur("1.26 m"), 1)

    def test_arrondir_une_grandeur_exacte(self):
        assert round(grandeur(1.26, "m"), 1).valeur == 1.3


class TestConversions:
    def test_vers_une_notation_de_manuel(self):
        assert grandeur(36, "km/h").vers("m.s-1").valeur == pytest.approx(10)

    def test_to_accepte_une_unite(self):
        assert grandeur(1, "km").to(unit("m")).valeur == 1000

    def test_conversion_affine(self):
        assert grandeur(20, "°C").vers("K").valeur == pytest.approx(293.15)

    def test_produit_avec_degres_celsius_passe_en_kelvins(self):
        rt = grandeur(8.314, "J/(mol*K)") * grandeur(20, "°C")
        assert rt.si().valeur == pytest.approx(8.314 * 293.15)

    @pytest.mark.parametrize(
        ("valeur", "unite", "attendu"),
        [
            (2.0, "kg.m.s-2", "2 N"),
            (1.0, "kN.mm", "1 J"),
            (6.0, "V/mA", "6000 Ω"),
            (1.0, "W.s", "1 J"),
            (2.0, "km/h", "0.555555555555556 m·s⁻¹"),
        ],
    )
    def test_si_simplifie(self, valeur, unite, attendu):
        assert str(grandeur(valeur, unite).si()) == attendu

    def test_unite_de_la_grandeur_compare_physiquement(self):
        f = grandeur("2.0 kg") * grandeur("9.81 m.s-2")
        assert f.unite == unit("N")

    def test_produit_par_une_unite(self):
        assert str(grandeur(2, "m") * unit("s")) == "2 m·s"
        assert str(grandeur(2, "m") / unit("s")) == "2 m·s⁻¹"


class TestEcriture:
    @pytest.mark.parametrize(
        ("g", "attendu"),
        [
            ("1.20 m.s-1", "(1.20 ± 0.01) m·s⁻¹"),
            ("1.20e3 kg.m-3", "(1.20 ± 0.01)e3 kg·m⁻³"),
            ("-0.5 K", "(-0.5 ± 0.1) K"),
        ],
    )
    def test_str_arrondit_d_apres_l_incertitude(self, g, attendu):
        assert str(grandeur(g)) == attendu

    def test_str_valeur_exacte(self):
        assert str(grandeur(9.81, "m/s2")) == "9.81 m·s⁻²"

    def test_degre_colle_au_nombre_mais_pas_le_celsius(self):
        assert str(grandeur(30, "°")) == "30°"
        assert str(grandeur(20, "°C")) == "20 °C"

    @pytest.mark.parametrize(
        ("options", "attendu"),
        [
            ({"style": "courte"}, "1.20(1) m"),
            ({"incertitude": False}, "1.20 m"),
            ({"decimale": ","}, "(1,20 ± 0,01) m"),
            ({"chiffres": 2}, "1.2 m"),
            ({"notation": "scientifique"}, "(1.20 ± 0.01) m"),
        ],
    )
    def test_texte_selon_les_options(self, options, attendu):
        assert grandeur("1.20 m").texte(**options) == attendu

    def test_texte_suit_les_reglages(self):
        with reglages_temporaires(style_incertitude="courte", decimale=","):
            assert str(grandeur("1.20 m")) == "1,20(1) m"

    def test_tableau_ecrit_avec_son_unite(self):
        assert str(grandeur(np.array([1.0, 2.0]), "m")) == "[1. 2.] m"

    def test_format_applique_a_la_valeur(self):
        assert f"{grandeur(1.23456, 'm'):.2f}" == "1.23 m"

    def test_format_pint_conserve(self):
        assert f"{grandeur(1.5, 'm/s'):~P}" == "1.5 m/s"

    def test_repr_lisible(self):
        assert repr(grandeur(1.5, "m")) == 'Grandeur(1.5, "meter")'

    def test_arrondi_d_un_tableau_refuse(self):
        with pytest.raises(TypeError):
            grandeur(np.array([1.0, 2.0]), "m").arrondi()


class TestReglesDePint:
    """Les règles de pint restent entières : aucun nombre nu n'est lu dans une unité."""

    @pytest.mark.parametrize(
        "calcul",
        [
            lambda lg: lg + 3,
            lambda lg: 3 - lg,
            lambda lg: lg < 13,
            lambda lg: np.add(lg, 3),
        ],
    )
    def test_nombre_nu_refuse(self, calcul):
        # pint lève DimensionalityError pour une somme, ValueError pour une comparaison.
        with pytest.raises((DimensionalityError, ValueError)):
            calcul(grandeur(12, "cm"))

    def test_zero_passe_comme_dans_pint(self):
        assert sum([grandeur(1, "m"), grandeur(2, "m")]).valeur == 3
        assert grandeur(1, "m") > 0

    def test_egalite_reste_celle_de_pint(self):
        assert grandeur(1, "m") != 1

    def test_dimensions_incompatibles_refusees(self):
        with pytest.raises(DimensionalityError):
            grandeur(1, "m") + grandeur(1, "s")

    def test_grandeur_sans_dimension_est_un_nombre(self, silence):
        assert (grandeur(3) + 2).valeur == 5
        assert (grandeur(1, "m") / grandeur(2, "m") + 1).valeur == 1.5

    def test_comparaisons_sur_les_valeurs_centrales(self):
        assert grandeur("1.20 m") < grandeur("1.21 m")
        assert grandeur("1.20 m") <= grandeur("1.20 m")
        assert grandeur(20, "°C") < grandeur(30, "°C")


def test_valeur_est_un_flottant():
    assert not isinstance(grandeur("1.20 m").valeur, UFloat)
