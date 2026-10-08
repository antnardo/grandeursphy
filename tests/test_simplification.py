import pytest

from grandeurs import unit, ureg
from grandeurs.simplification import SimplificateurSI, simplificateur


@pytest.mark.parametrize(
    ("unite", "attendu"),
    [
        ("kg.m.s-2", "N"),
        ("N.m", "J"),
        ("kg.m2.s-3", "W"),
        ("kg.m-1.s-2", "Pa"),
        ("A.s", "C"),
        ("kg.m2.s-3.A-1", "V"),
        ("V/A", "Ω"),
        ("J/K", "J·K⁻¹"),
        ("J/(mol*K)", "J·mol⁻¹·K⁻¹"),
        ("W/(m*K)", "W·m⁻¹·K⁻¹"),
        ("kg/s^3", "W·m⁻²"),
        ("V/m", "V·m⁻¹"),
        ("N/A^2", "H·m⁻¹"),
        ("C^2*m^2/J", "F·m²"),
        ("Ω*m", "Ω·m"),
        ("J*s", "J·s"),
    ],
)
def test_unite_derivee_la_plus_courte(unite, attendu):
    assert str(unit(unite).si()) == attendu


@pytest.mark.parametrize(
    ("unite", "attendu"),
    [
        ("m/s^2", "m·s⁻²"),  # jamais N/kg : ni masse ni courant
        ("m^2/s", "m²·s⁻¹"),
        ("Hz", "s⁻¹"),  # Hz, Bq ou rad/s : on ne choisit pas
        ("J/kg", "m²·s⁻²"),
        ("mol/L", "mol·m⁻³"),
        ("kg/m^3", "kg·m⁻³"),  # les unités de base gagnent à égalité
        ("kg*m^2", "kg·m²"),
        ("km/h", "m·s⁻¹"),
    ],
)
def test_sans_masse_ni_courant_reste_en_unites_de_base(unite, attendu):
    assert str(unit(unite).si()) == attendu


def test_radian_garde():
    assert str(unit("rad/s").si()) == "rad·s⁻¹"


def test_simplifier_convertit_la_valeur():
    q = ureg.Quantity(1, "kN.mm")
    assert simplificateur(ureg).simplifier(q).m == pytest.approx(1.0)
    assert str(simplificateur(ureg).simplifier(q).units) == "J"


def test_liste_de_derivees_choisie():
    seul_newton = SimplificateurSI(ureg, derivees=("newton",))
    assert dict(seul_newton.unites(ureg.parse_units("J")._units)) == {"newton": 1, "meter": 1}
