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
        (r"\qty{1.20(1)}{m.s^{-1}}", "(1.20 ± 0.02) m·s⁻¹"),
        (r"\qty{1,20(1)e3}{kg.m^{-3}}", "(1.20 ± 0.02)e3 kg·m⁻³"),
        (r"\qty{5(1)}{\micro\ohm}", "(5 ± 2) µΩ"),
        (r"\qty{20.0}{\degreeCelsius}", "(20.0 ± 0.2) °C"),
        (r"\qty[per-mode=symbol]{3}{\micro m}", "(3 ± 2) µm"),
        (r"\SI{2}{k\ohm}", "(2 ± 2) kΩ"),
        (r"\qty{1}{J.mol^{-1}.K^{-1}}", "(1 ± 2) J·mol⁻¹·K⁻¹"),
        (r"\num{0.50}", "0.50 ± 0.02"),
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


@pytest.mark.parametrize(
    ("appel", "attendu"),
    [
        (lambda: qty(grandeur("1.20 m"), style="pm"), r"\qty{1.20 \pm 0.02}{m}"),
        (lambda: qty(grandeur("1.20e3 kg.m-3"), style="pm"), r"\qty{1.20 \pm 0.02 e3}{kg.m^{-3}}"),
        (lambda: qty(grandeur("-0.5 K"), style="pm"), r"\qty{-0.5 \pm 0.2}{K}"),
        (lambda: qty(grandeur("1.20 m"), style="pm", decimale=","), r"\qty{1,20 \pm 0,02}{m}"),
        (
            lambda: qty(grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.02]), style="pm"),
            r"\qtylist{1.0 \pm 0.2;2.00 \pm 0.04}{m}",
        ),
        (lambda: num(ufloat(1.234, 0.012), style="pm"), r"\num{1.23 \pm 0.02}"),
        (lambda: qty(grandeur(2, "m"), style="pm"), r"\qty{2.00}{m}"),
        (lambda: qty(grandeur("1.20 m"), style="pm", incertitude=False), r"\qty{1.20}{m}"),
    ],
)
def test_qty_style_pm(appel, attendu):
    assert appel() == attendu


@pytest.mark.parametrize(
    ("appel", "attendu"),
    [
        (lambda: qty(grandeur("1.20 m"), style="u"), r"x = \qty{1.20}{m} ; u(x) = \qty{0.01}{m}"),
        (lambda: qty(grandeur("1.20 m"), style="U"), r"x = \qty{1.20}{m} ; U(x) = \qty{0.02}{m}"),
        (
            lambda: qty(grandeur("1.20 m"), style="U", nom="v", decimale=","),
            r"v = \qty{1,20}{m} ; U(v) = \qty{0,02}{m}",
        ),
        (
            lambda: qty(grandeur("1.20e3 kg.m-3"), style="u"),
            r"x = \qty{1.20e3}{kg.m^{-3}} ; u(x) = \qty{0.01e3}{kg.m^{-3}}",
        ),
        (
            lambda: qty(grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.02]), style="U"),
            r"x = \qtylist{1.0;2.00}{m} ; U(x) = \qtylist{0.2;0.04}{m}",
        ),
        (lambda: qty(grandeur(2, "m"), style="u"), r"x = \qty{2.00}{m}"),
        (lambda: qty(grandeur("1.20 m"), style="U", incertitude=False), r"x = \qty{1.20}{m}"),
        (lambda: num(ufloat(1.234, 0.012), style="u"), r"x = \num{1.23} ; u(x) = \num{0.01}"),
        (lambda: num(ufloat(1.234, 0.012), style="U"), r"x = \num{1.23} ; U(x) = \num{0.02}"),
        (lambda: num(0.5, style="u", nom="e"), r"e = \num{0.500}"),
    ],
)
def test_qty_styles_nommes(appel, attendu):
    assert appel() == attendu


def test_k_a_l_appel():
    g = grandeur("1.20 m")
    assert qty(g, style="pm", k=3) == r"\qty{1.20 \pm 0.03}{m}"
    assert qty(g, style="U", k=3) == r"x = \qty{1.20}{m} ; U(x) = \qty{0.03}{m}"
    assert qty(g, k=3) == r"\qty{1.20(1)}{m}"
    with reglages_temporaires(facteur_elargissement=3):
        assert qty(g, style="pm", k=1) == r"\qty{1.20 \pm 0.01}{m}"
    assert num(ufloat(1.234, 0.012), style="pm", k=1) == r"\num{1.23 \pm 0.01}"


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        (r"\qty{1.20 \pm 0.04}{m}", "(1.20 ± 0.04) m"),
        (r"\qty{1.20 \pm 0.04 e3}{m}", "(1.20 ± 0.04)e3 m"),
        (r"\qty{1.20\pm0.04}{m}", "(1.20 ± 0.04) m"),
        (r"\num{1,20 \pm 0,04}", "1.20 ± 0.04"),
    ],
)
def test_lire_qty_pm(texte, attendu):
    assert str(lire_qty(texte)) == attendu


@pytest.mark.parametrize(
    ("texte", "incertitude"),
    [
        (r"x = \qty{1.20}{m} ; u(x) = \qty{0.04}{m}", 0.04),
        (r"x = \qty{1.20}{m} ; U(x) = \qty{0.04}{m}", 0.02),
        (r"L = \qty{1.20}{m} ; u(L) = \qty{4}{cm}", 0.04),
        (r"x = \qty{1.20e3}{kg.m^{-3}} ; U(x) = \qty{0.02e3}{kg.m^{-3}}", 10),
        (r"x = \num{0.500} ; u(x) = \num{0.002}", 0.002),
    ],
)
def test_lire_qty_styles_nommes(texte, incertitude):
    g = lire_qty(texte)
    assert g.incertitude == pytest.approx(incertitude)
    assert g.valeur == pytest.approx(lire_qty(texte.split(" ; ")[0].split(" = ")[1]).valeur)


@pytest.mark.parametrize("style", ["pm", "courte", "u", "U"])
@pytest.mark.parametrize(
    "g",
    [
        grandeur(1.2, "m", incertitude=0.05),
        grandeur(1230, "kg.m-3", incertitude=10),
        grandeur("-0.5 K"),
        grandeur(2.0, "m", incertitude=0.02),
        grandeur(0.5, "", incertitude=0.003),
    ],
)
def test_aller_retour_qty_lire_qty_dans_les_quatre_styles(g, style):
    relu = lire_qty(qty(g, style=style))
    assert relu.unite == g.unite
    assert relu.valeur == pytest.approx(g.valeur)
    assert relu.incertitude == pytest.approx(g.incertitude)


def test_qty_garde_l_incertitude_type_quel_que_soit_le_facteur():
    g = grandeur("1.20 m")
    assert qty(g) == r"\qty{1.20(1)}{m}"
    with reglages_temporaires(facteur_elargissement=3):
        assert qty(g) == r"\qty{1.20(1)}{m}"


def test_lire_qty_parentheses_en_u_et_pm_en_incertitude_elargie():
    assert lire_qty(r"\qty{1.20(3)}{m}").incertitude == pytest.approx(0.03)
    assert lire_qty(r"\qty{1.20 +- 0.03}{m}").incertitude == pytest.approx(0.015)


def test_aller_retour_qty_lire_qty():
    g = grandeur(1.234, "m", incertitude=0.06)
    relu = lire_qty(qty(g))
    assert relu.incertitude == pytest.approx(0.06)
