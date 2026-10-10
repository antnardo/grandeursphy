import numpy as np
import pytest
from uncertainties import ufloat

from grandeurs import constantes as cst
from grandeurs import grandeur, lire_qty, num, qty, reglages_temporaires, unite_siunitx


@pytest.mark.parametrize(
    ("g", "attendu"),
    [
        (grandeur("1.20 m.s-1"), r"\qty{1.20(1)}{m.s^{-1}}"),
        (grandeur("1.20e3 kg.m-3"), r"\qty{1.20(1)e3}{kg.m^{-3}}"),
        (grandeur(20, "°C"), r"\qty{20.0}{\degreeCelsius}"),
        (grandeur("5 µΩ"), r"\qty{5(1)}{\micro\ohm}"),
        (grandeur(9.81, "m/s2"), r"\qty{9.81}{m.s^{-2}}"),
        (cst.EPS_0, r"\qty{8.854187819(1)e-12}{F.m^{-1}}"),
    ],
)
def test_qty(g, attendu):
    assert qty(g) == attendu


def test_qty_virgule_francaise():
    assert qty(grandeur("1.20e3 kg.m-3"), decimale=",") == r"\qty{1,20(1)e3}{kg.m^{-3}}"


def test_qty_suit_le_reglage_decimal():
    with reglages_temporaires(decimale=","):
        assert qty(grandeur("1.20 m")) == r"\qty{1,20(1)}{m}"


def test_qty_sans_incertitude_garde_les_chiffres_significatifs():
    assert qty(grandeur("1.20 m"), incertitude=False) == r"\qty{1.20}{m}"


def test_qty_a_n_chiffres():
    rt = (cst.R_GP * grandeur(300, "K")).si()
    assert qty(rt) == r"\qty{2.49e3}{J.mol^{-1}}"
    assert qty(rt, chiffres=5) == r"\qty{2494.3}{J.mol^{-1}}"


def test_qty_et_num_suivent_le_reglage_chiffres():
    with reglages_temporaires(chiffres=4):
        assert qty(grandeur(9.79828445167129, "m/s2")) == r"\qty{9.798}{m.s^{-2}}"
        assert num(6.02214076e23) == r"\num{6.022e23}"


def test_qty_convertit_d_abord():
    assert qty(grandeur("1.20 m.s-1"), "km/h") == r"\qty{4.32(4)}{km.h^{-1}}"


def test_qty_ancienne_macro():
    assert qty(grandeur(2, "m"), macro="SI") == r"\SI{2.00}{m}"


def test_qty_d_une_chaine():
    assert qty("1.20 m") == r"\qty{1.20(1)}{m}"


def test_qty_d_un_tableau_donne_une_liste():
    assert qty(grandeur(np.array([1.0, 2.5]), "m")) == r"\qtylist{1.00;2.50}{m}"


def test_qty_sans_unite_donne_num():
    assert qty(grandeur(0.5, "")) == r"\num{0.500}"


def test_qty_tableau_a_deux_dimensions_refuse():
    with pytest.raises(TypeError):
        qty(grandeur(np.ones((2, 2)), "m"))


@pytest.mark.parametrize(
    ("x", "attendu"),
    [
        (0.5, r"\num{0.500}"),
        (ufloat(1.234, 0.012), r"\num{1.23(1)}"),
        (cst.ALPHA, r"\num{0.007297352564(1)}"),
        (6.02214076e23, r"\num{6.02e23}"),
    ],
)
def test_num(x, attendu):
    assert num(x) == attendu


def test_num_refuse_une_grandeur_dimensionnee():
    with pytest.raises(TypeError, match="qty"):
        num(grandeur(1, "m"))


def test_unite_siunitx():
    assert unite_siunitx("J.mol-1.K-1") == "J.mol^{-1}.K^{-1}"


def test_methode_latex_de_la_grandeur():
    assert grandeur("1.20 m").latex(decimale=",") == r"\qty{1,20(1)}{m}"


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        (r"\qty{1.20(1)}{m.s^{-1}}", "(1.20 ± 0.01) m·s⁻¹"),
        (r"\qty{1,20(1)e3}{kg.m^{-3}}", "(1.20 ± 0.01)e3 kg·m⁻³"),
        (r"\qty{5(1)}{\micro\ohm}", "(5 ± 1) µΩ"),
        (r"\qty{20.0}{\degreeCelsius}", "(20.0 ± 0.1) °C"),
        (r"\qty[per-mode=symbol]{3}{\micro m}", "(3 ± 1) µm"),
        (r"\SI{2}{k\ohm}", "(2 ± 1) kΩ"),
        (r"\qty{1}{J.mol^{-1}.K^{-1}}", "(1 ± 1) J·mol⁻¹·K⁻¹"),
        (r"\num{0.50}", "0.50 ± 0.01"),
    ],
)
def test_lire_qty(texte, attendu):
    assert str(lire_qty(texte)) == attendu


@pytest.mark.parametrize("texte", [r"\qty{1}", r"\si{m}", "1.20 m"])
def test_lire_qty_refuse_autre_chose(texte):
    with pytest.raises(ValueError):
        lire_qty(texte)


@pytest.mark.parametrize(
    "g",
    [
        grandeur("1.20 m.s-1"),
        grandeur("1.20e3 kg.m-3"),
        grandeur("5 µΩ"),
        grandeur("20.0 °C"),
        cst.EPS_0,
        grandeur(9.81, "m/s2"),
    ],
)
def test_lire_qty_inverse_de_qty(g):
    relu = lire_qty(qty(g))
    assert relu.unite == g.unite
    assert relu.valeur == pytest.approx(g.valeur, rel=1e-9)
