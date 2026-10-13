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
            (2.0, "kg.m.s-2", "2.00 N"),
            (1.0, "kN.mm", "1.00 J"),
            (6.0, "V/mA", "6.00e3 Ω"),
            (1.0, "W.s", "1.00 J"),
            (2.0, "km/h", "0.556 m·s⁻¹"),
        ],
    )
    def test_si_simplifie(self, valeur, unite, attendu):
        assert str(grandeur(valeur, unite).si()) == attendu

    def test_unite_de_la_grandeur_compare_physiquement(self):
        f = grandeur("2.0 kg") * grandeur("9.81 m.s-2")
        assert f.unite == unit("N")


class TestEcriture:
    @pytest.mark.parametrize(
        ("g", "attendu"),
        [
            ("1.20 m.s-1", "(1.20 ± 0.02) m·s⁻¹"),
            ("1.20e3 kg.m-3", "(1.20 ± 0.02)e3 kg·m⁻³"),
            ("-0.5 K", "(-0.5 ± 0.2) K"),
        ],
    )
    def test_str_arrondit_d_apres_l_incertitude(self, g, attendu):
        assert str(grandeur(g)) == attendu

    def test_str_valeur_exacte(self):
        assert str(grandeur(9.81, "m/s2")) == "9.81 m·s⁻²"

    def test_degre_colle_au_nombre_mais_pas_le_celsius(self):
        assert str(grandeur(30, "°")) == "30.0°"
        assert str(grandeur(20, "°C")) == "20.0 °C"

    @pytest.mark.parametrize(
        ("options", "attendu"),
        [
            ({"style": "courte"}, "1.20(1) m"),
            ({"incertitude": False}, "1.20 m"),
            ({"decimale": ","}, "(1,20 ± 0,02) m"),
            ({"chiffres": 2}, "1.2 m"),
            ({"notation": "scientifique"}, "(1.20 ± 0.02) m"),
        ],
    )
    def test_texte_selon_les_options(self, options, attendu):
        assert grandeur("1.20 m").texte(**options) == attendu

    def test_texte_suit_les_reglages(self):
        with reglages_temporaires(style_incertitude="courte", decimale=","):
            assert str(grandeur("1.20 m")) == "1,20(1) m"

    def test_tableau_arrondi_comme_un_scalaire(self):
        assert str(grandeur(np.array([1.0, 2.0]), "m")) == "[1.00; 2.00] m"
        assert str(grandeur(np.ones((2, 2)), "m")) == "[[1.00; 1.00];\n [1.00; 1.00]] m"

    def test_tableau_incertain_arrondi_d_apres_les_incertitudes(self):
        g = grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.02])
        assert str(g) == "[1.0 ± 0.2; 2.00 ± 0.04] m"
        assert g.texte(style="courte") == "[1.0(1); 2.00(2)] m"

    def test_valeur_exacte_au_reglage_chiffres(self):
        g = grandeur(9.79828445167129, "m/s2")
        assert str(g) == "9.80 m·s⁻²"
        with reglages_temporaires(chiffres=5):
            assert str(g) == "9.7983 m·s⁻²"
        assert g.texte(chiffres=2) == "9.8 m·s⁻²"

    def test_pm_ecrit_l_incertitude_elargie_et_courte_l_incertitude_type(self):
        g = grandeur(1.2, "m", incertitude=0.01)
        assert g.incertitude == 0.01
        assert g.texte(style="pm") == "(1.20 ± 0.02) m"
        assert g.texte(style="courte") == "1.20(1) m"

    @pytest.mark.parametrize(
        ("options", "attendu"),
        [
            ({"style": "u"}, "x = 1.20 m ; u(x) = 0.01 m"),
            ({"style": "U"}, "x = 1.20 m ; U(x) = 0.02 m"),
            ({"style": "u", "nom": "L"}, "L = 1.20 m ; u(L) = 0.01 m"),
            ({"style": "U", "decimale": ","}, "x = 1,20 m ; U(x) = 0,02 m"),
            ({"style": "U", "k": 3}, "x = 1.20 m ; U(x) = 0.03 m"),
            ({"style": "u", "k": 3}, "x = 1.20 m ; u(x) = 0.01 m"),
            ({"style": "pm", "k": 3}, "(1.20 ± 0.03) m"),
            ({"style": "courte", "k": 3}, "1.20(1) m"),
            ({"style": "u", "incertitude": False}, "x = 1.20 m"),
            ({"style": "U", "chiffres": 2}, "x = 1.2 m"),
            ({"style": "U", "notation": "scientifique"}, "x = 1.20 m ; U(x) = 0.02 m"),
        ],
    )
    def test_styles_nommes_et_k_a_l_appel(self, options, attendu):
        assert grandeur("1.20 m").texte(**options) == attendu

    @pytest.mark.parametrize(
        ("g", "style", "attendu"),
        [
            (grandeur("1.20e3 kg.m-3"), "U", "x = 1.20e3 kg·m⁻³ ; U(x) = 0.02e3 kg·m⁻³"),
            (grandeur("1.20e3 kg.m-3"), "u", "x = 1.20e3 kg·m⁻³ ; u(x) = 0.01e3 kg·m⁻³"),
            (grandeur(2, "m"), "u", "x = 2.00 m"),
            (grandeur("30.0 °"), "U", "x = 30.0° ; U(x) = 0.2°"),
            (grandeur("0.500", ""), "u", "x = 0.500 ; u(x) = 0.001"),
            (grandeur(1.234, "m", incertitude=0.06), "u", "x = 1.23 m ; u(x) = 0.06 m"),
            (grandeur(1.234, "m", incertitude=0.06), "U", "x = 1.2 m ; U(x) = 0.1 m"),
            (
                grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.02]),
                "u",
                "x = [1.0; 2.00] m ; u(x) = [0.1; 0.02] m",
            ),
            (
                grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.02]),
                "U",
                "x = [1.0; 2.00] m ; U(x) = [0.2; 0.04] m",
            ),
            (grandeur(np.array([1.0, 2.0]), "m"), "U", "x = [1.00; 2.00] m"),
        ],
    )
    def test_styles_nommes_selon_la_grandeur(self, g, style, attendu):
        assert g.texte(style=style) == attendu

    @pytest.mark.parametrize(
        ("style", "attendu"),
        [("u", "x = 1.20 m ; u(x) = 0.01 m"), ("U", "x = 1.20 m ; U(x) = 0.02 m")],
    )
    def test_str_suit_le_style_nomme_du_reglage(self, style, attendu):
        with reglages_temporaires(style_incertitude=style):
            assert str(grandeur("1.20 m")) == attendu

    @pytest.mark.parametrize(
        "texte", ["1.20 m", "(1.20 ± 0.02) m", "1.20(1) m", "(5.0 ± 0.4)e3 Pa", "-0.5 K"]
    )
    @pytest.mark.parametrize("style", ["pm", "courte", "u", "U"])
    def test_aller_retour_str_grandeur(self, texte, style):
        g = grandeur(texte)
        relu = grandeur(g.texte(style=style))
        assert relu.valeur == pytest.approx(g.valeur)
        assert relu.incertitude == pytest.approx(g.incertitude)
        assert relu.texte(style=style) == g.texte(style=style)

    def test_facteur_d_elargissement_reglable(self):
        g = grandeur("1.20 m")
        with reglages_temporaires(facteur_elargissement=3):
            assert str(g) == "(1.20 ± 0.03) m"
            assert grandeur("1.20 ± 0.03 m").incertitude == pytest.approx(0.01)
            assert g.texte(style="courte") == "1.20(1) m"
        assert grandeur("1.20 ± 0.03 m").incertitude == pytest.approx(0.015)

    def test_arrondi_elargi(self):
        g = grandeur(1.234, "m", incertitude=0.06)
        assert g.arrondi().ecrire() == "1.23(6)"
        assert g.arrondi(elargie=True).ecrire() == "1.2 ± 0.1"
        assert g.arrondi(elargie=True, k=1).ecrire() == "1.23 ± 0.06"
        assert g.arrondi(elargie=True, k=3).ecrire() == "1.2 ± 0.2"

    def test_valeur_incertaine_ignore_le_reglage_chiffres(self):
        with reglages_temporaires(chiffres=5):
            assert str(grandeur("1.20 m")) == "(1.20 ± 0.02) m"

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


@pytest.mark.parametrize(
    "texte", ["1.20 m.s-1", "1.20e3 kg.m-3", "-0.5 K", "5 µΩ", "20.0 °C", "1.20(3) J.mol-1.K-1"]
)
def test_grandeur_relit_ce_que_texte_ecrit(texte):
    g = grandeur(texte)
    relu = grandeur(str(g))
    assert relu.unite == g.unite
    assert (relu.valeur, relu.incertitude) == pytest.approx((g.valeur, g.incertitude))
