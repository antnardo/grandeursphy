import pytest

from grandeurs import Grandeur, Unite, unit, ureg


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


def test_egalite_avec_chaine_et_unite_pint():
    assert unit("J") == "N.m"
    assert unit("N") == ureg.Unit("kilogram * meter / second ** 2")


def test_identique_compare_l_ecriture():
    assert not unit("N").identique("kg.m.s-2")
    assert unit("N").identique("newton")


def test_hachage_coherent_avec_l_egalite():
    assert len({unit("N"), unit("kg.m.s-2"), unit("J")}) == 2


def test_comparaison_a_un_autre_type_est_fausse():
    assert unit("m") != 3
    assert unit("m") != "pas une unité"


@pytest.mark.parametrize(
    ("texte", "facteur", "decalage"),
    [("km", 1000.0, 0.0), ("°C", 1.0, 273.15), ("°F", 5 / 9, 255.3722222222222), ("mL", 1e-6, 0.0)],
)
def test_facteur_et_decalage_vers_le_si(texte, facteur, decalage):
    u = unit(texte)
    assert u.facteur_si == pytest.approx(facteur)
    assert u.decalage_si == pytest.approx(decalage)


def test_unite_affine_reconnue():
    assert unit("°C").affine
    assert not unit("K").affine


def test_dimension_selon_pint():
    assert unit("m/s").dimension == "[length] / [time]"
    assert unit("rad").sans_dimension


def test_si_simplifie_en_unite_derivee():
    assert unit("kg.m.s-2").si().identique("N")


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [("m.s-1", "m·s⁻¹"), ("J/(mol*K)", "J·mol⁻¹·K⁻¹"), ("L", "L"), ("°C", "°C")],
)
def test_ecriture_texte(texte, attendu):
    assert str(unit(texte)) == attendu


def test_repr_relisible():
    assert repr(unit("m.s-1")) == "unit('m·s⁻¹')"
    assert eval(repr(unit("m.s-1"))) == unit("m/s")


def test_algebre_des_unites():
    assert unit("m") / "s" == unit("m.s-1")
    assert unit("m") * unit("s-1") == unit("m/s")
    assert unit("m") ** 2 == unit("m2")
    assert isinstance(unit("m") / "s", Unite)


def test_nombre_fois_unite_donne_une_grandeur():
    g = 3 * unit("m")
    assert isinstance(g, Grandeur)
    assert str(g) == "3 m"
    assert str(unit("m") * 3) == "3 m"
    assert str(1 / unit("s")) == "1 s⁻¹"
