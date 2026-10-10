import pytest

from grandeurs import Unite, equivalentes, grandeur, unit, ureg


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("N", "kg.m.s^(-2)"),
        ("N", "kg*m/s**2"),
        ("N", "kg·m·s⁻²"),
        ("J", "N.m"),
        ("J", "kg.m2.s-2"),
        ("W", "J/s"),
        ("Pa", "N/m^2"),
        ("C", "A.s"),
        ("V", "W/A"),
        ("Ω", "V/A"),
        ("F", "C/V"),
        ("T", "Wb/m2"),
        ("H", "Wb/A"),
        ("L", "dm3"),
        ("mL", "cm^3"),
        ("M", "mol.L-1"),
        ("J.mol-1.K-1", "J/(mol*K)"),
        ("µm", "um"),
        ("°C", "degC"),
        ("delta_degC", "K"),
    ],
)
def test_unites_egales_physiquement(a, b):
    assert unit(a) == unit(b)
    assert equivalentes(a, b)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("Hz", "Bq"),  # même dimension, facteur 1 : le SI ne les distingue pas
        ("Hz", "rad/s"),  # le radian est sans dimension
        ("rad", ""),
        ("sr", ""),
    ],
)
def test_cas_limites_du_si_egaux(a, b):
    assert unit(a) == unit(b)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("km", "m"),
        ("°C", "K"),  # unité affine : 0 °C n'est pas 0 K
        ("°", "rad"),
        ("°", ""),
        ("%", ""),
        ("eV", "J"),
        ("N", "J"),
    ],
)
def test_unites_differentes(a, b):
    assert unit(a) != unit(b)
    assert not equivalentes(a, b)


def test_egalite_avec_chaine_et_unite_pint():
    assert unit("J") == "N.m"
    assert unit("N") == ureg.Unit("kilogram * meter / second ** 2")
    assert equivalentes(unit("N"), ureg.Unit("newton"))


def test_equivalentes_refuse_autre_chose_qu_une_unite():
    with pytest.raises(TypeError, match="pas une unité"):
        equivalentes("m", 3)


def test_hachage_coherent_avec_l_egalite():
    assert len({unit("N"), unit("kg.m.s-2"), unit("J")}) == 2


def test_comparaison_a_un_autre_type_est_fausse():
    assert unit("m") != 3
    assert unit("m") != "pas une unité"


def test_unite_d_une_grandeur():
    f = grandeur("2.0 kg") * grandeur("9.81 m.s-2")
    assert isinstance(f.unite, Unite)
    assert f.unite == unit("N")
    assert grandeur(1, "km").to(unit("m")).valeur == 1000


@pytest.mark.parametrize(
    ("texte", "style", "attendu"),
    [
        ("m.s-1", "texte", "m·s⁻¹"),
        ("J/(mol*K)", "texte", "J·mol⁻¹·K⁻¹"),
        ("L", "texte", "L"),
        ("°C", "texte", "°C"),
        ("m.s-1", "ascii", "m.s-1"),
        ("J.mol-1.K-1", "siunitx", "J.mol^{-1}.K^{-1}"),
        ("µΩ", "siunitx", r"\micro\ohm"),
    ],
)
def test_ecriture(texte, style, attendu):
    assert unit(texte).ecrire(style) == attendu


def test_str_et_repr_relisibles():
    assert str(unit("m.s-1")) == "m·s⁻¹"
    assert repr(unit("m.s-1")) == "unit('m·s⁻¹')"
    assert eval(repr(unit("m.s-1"))) == unit("m/s")
