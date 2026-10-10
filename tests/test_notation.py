import pytest

from grandeurs.notation import traduire_notation


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        ("m.s-1", "m*s**(-1)"),
        ("m·s⁻¹", "m*s**(-1)"),
        ("kg.m.s^(-2)", "kg*m*s**(-2)"),
        ("kg m s^-2", "kg*m*s**(-2)"),
        ("mol.L-1", "mol*L**(-1)"),
        ("J.mol-1.K-1", "J*mol**(-1)*K**(-1)"),
        ("m2", "m**(2)"),
        ("m/s²", "m/(s**(2))"),
        ("m^0.5", "m**(0.5)"),
        ("kg*m/s**2", "kg*m/(s**(2))"),
        ("1/s", "1/(s)"),
        ("C_90 mol^-1", "C_90*mol**(-1)"),
        ("(GeV/c^2)^-2", "(GeV/(c**(2)))**(-2)"),
    ],
)
def test_traduire_notation_de_manuel_donne_syntaxe_pint(texte, attendu):
    assert traduire_notation(texte) == attendu


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        ("J/mol.K", "J/(mol*K)"),
        ("W/m.K", "W/(m*K)"),
        ("J / mol K", "J/(mol*K)"),
        ("J/mol/K", "J/(mol)/(K)"),
    ],
)
def test_produit_faible_apres_barre_reste_au_denominateur(texte, attendu):
    assert traduire_notation(texte) == attendu


def test_etoile_apres_barre_garde_la_priorite_de_python():
    assert traduire_notation("J/mol*K") == "J/(mol)*K"


@pytest.mark.parametrize("texte", ["µm", "°C", "L", "mL", "Ω", "delta_degC", "E_h", ""])
def test_nom_seul_inchange(texte):
    assert traduire_notation(texte) == texte


@pytest.mark.parametrize(("variante", "forme"), [("μm", "µm"), ("Ω", "Ω"), ("Å", "Å")])
def test_variantes_unicode_ramenees_a_une_forme(variante, forme):
    assert traduire_notation(variante) == forme


def test_nombre_decimal_non_confondu_avec_un_produit():
    assert traduire_notation("1.20e3 m") == "1.20e3*m"


@pytest.mark.parametrize("texte", ["[length]", "3 m + 2 cm", "-1 m", "m^{-1}", "m^(1/2)"])
def test_texte_hors_grammaire_rendu_tel_quel(texte):
    assert traduire_notation(texte) == texte
