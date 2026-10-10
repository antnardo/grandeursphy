import math

import pytest

from grandeurs import grandeur, ureg
from grandeurs.affichage import formateur
from grandeurs.simplification import PREFEREES_SI, SimplificateurSI, simplificateur


def si(texte: str) -> str:
    """Écriture SI simplifiée d'une unité donnée en notation de manuel."""
    conteneur = simplificateur(ureg).unites(ureg.parse_units(texte)._units)
    return formateur(ureg).ecrire(conteneur)


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
        ("C.m", "C·m"),
    ],
)
def test_unite_derivee_la_plus_courte(unite, attendu):
    assert si(unite) == attendu


@pytest.mark.parametrize(
    ("unite", "attendu"),
    [
        ("N/m", "N·m⁻¹"),  # et non T·A
        ("kg.s-2", "N·m⁻¹"),
        ("S/m", "S·m⁻¹"),  # et non Ω⁻¹·m⁻¹
        ("mS/cm", "S·m⁻¹"),
        ("C/kg", "C·kg⁻¹"),  # et non T⁻¹·s⁻¹
        ("lm", "lm"),  # et non cd·rad²
        ("lx", "lx"),
        ("Bq", "Bq"),  # et non count·s⁻¹
        ("kBq", "Bq"),
        ("A/m", "A·m⁻¹"),
        ("Pa.s", "Pa·s"),
        ("J/(kg.K)", "J·kg⁻¹·K⁻¹"),
        ("N/C", "V·m⁻¹"),
        ("J/mol", "J·mol⁻¹"),
    ],
)
def test_cas_absurdes_de_l_audit_par_la_table(unite, attendu):
    assert si(unite) == attendu


@pytest.mark.parametrize(
    ("unite", "attendu"),
    [
        ("m/s^2", "m·s⁻²"),  # jamais N/kg : ni masse ni courant
        ("m^2/s", "m²·s⁻¹"),
        ("J/kg", "m²·s⁻²"),  # Gy et Sv ne sont pas choisis
        ("mGy", "m²·s⁻²"),
        ("mol/L", "mol·m⁻³"),
        ("kg/m^3", "kg·m⁻³"),  # les unités de base gagnent à égalité
        ("kg*m^2", "kg·m²"),
        ("km/h", "m·s⁻¹"),
        ("cd/m^2", "cd·m⁻²"),
    ],
)
def test_sans_masse_ni_courant_reste_en_unites_de_base(unite, attendu):
    assert si(unite) == attendu


@pytest.mark.parametrize("unite", ["Hz", "kHz", "1/s", "rad/s", "tr/min"])
def test_le_hertz_n_est_jamais_choisi(unite):
    assert "Hz" not in si(unite)


def test_frequence_angulaire_en_radians_par_seconde():
    omega = grandeur(2 * math.pi, "rad") * grandeur(50, "Hz")
    assert str(omega.si().unite) == "rad·s⁻¹"
    assert str((grandeur(1, "rad") / grandeur(2, "ms")).si().unite) == "rad·s⁻¹"
    assert str((1 / grandeur(2, "ms")).si().unite) == "s⁻¹"


def test_simplifier_convertit_la_valeur():
    q = ureg.Quantity(1, "kN.mm")
    assert simplificateur(ureg).simplifier(q).m == pytest.approx(1.0)
    assert str(simplificateur(ureg).simplifier(q).units) == "J"


def test_table_sans_doublon():
    assert len(PREFEREES_SI) == len(set(PREFEREES_SI))
    with pytest.raises(ValueError, match="même écriture"):
        SimplificateurSI(ureg, preferees=("V/m", "N/C"))


def test_liste_de_derivees_choisie():
    seul_newton = SimplificateurSI(ureg, derivees=("newton",), preferees=())
    assert dict(seul_newton.unites(ureg.parse_units("J")._units)) == {"newton": 1, "meter": 1}
