import pytest

from grandeurs import ureg
from grandeurs.affichage import formateur


@pytest.fixture
def ecrire():
    f = formateur(ureg)
    return lambda texte, style="texte": f.ecrire(ureg.parse_units(texte), style)


@pytest.mark.parametrize(
    ("unite", "attendu"),
    [
        ("m.s-1", "m·s⁻¹"),
        ("m/s^2", "m·s⁻²"),
        ("J/(mol*K)", "J·mol⁻¹·K⁻¹"),
        ("s-1.m", "m·s⁻¹"),  # exposants positifs d'abord
        ("L", "L"),
        ("mL", "mL"),
        ("µm", "µm"),
        ("kΩ", "kΩ"),
        ("deg", "°"),
        ("m^0.5", "m^0.5"),
        ("", ""),
    ],
)
def test_ecriture_texte(ecrire, unite, attendu):
    assert ecrire(unite) == attendu


@pytest.mark.parametrize(
    ("unite", "attendu"),
    [("m.s-1", "m.s-1"), ("kg.m2", "kg.m2"), ("m^0.5", "m^0.5")],
)
def test_ecriture_ascii_relisible(ecrire, unite, attendu):
    assert ecrire(unite, "ascii") == attendu
    assert ureg.parse_units(attendu) == ureg.parse_units(unite)


@pytest.mark.parametrize(
    ("unite", "attendu"),
    [
        ("kg.m-3", "kg.m^{-3}"),
        ("J.mol-1.K-1", "J.mol^{-1}.K^{-1}"),
        ("µm", r"\micro m"),
        ("µΩ", r"\micro\ohm"),
        ("kΩ", r"k\ohm"),
        ("Ω.m", r"\ohm.m"),
        ("°C", r"\degreeCelsius"),
        ("deg", r"\degree"),
        ("%", r"\percent"),
        ("Å", r"\angstrom"),
        ("L", "L"),
    ],
)
def test_ecriture_siunitx_litterale(ecrire, unite, attendu):
    assert ecrire(unite, "siunitx") == attendu


def test_symboles_separent_prefixe_et_base():
    assert list(formateur(ureg).symboles(ureg.parse_units("km.s-1"))) == [
        ("k", "m", 1),
        ("", "s", -1),
    ]
