import math

import pytest

from grandeurs import Grandeur, unit
from grandeurs import constantes as cst

# Valeurs CODATA 2022 (https://physics.nist.gov/cuu/Constants/), recopiées ici
# pour que le passage de scipy à une autre édition se voie.
CODATA_2022 = [
    ("C", 299792458, 0, "m/s"),
    ("H", 6.62607015e-34, 0, "J/Hz"),
    ("E", 1.602176634e-19, 0, "C"),
    ("KB", 1.380649e-23, 0, "J/K"),
    ("NA", 6.02214076e23, 0, "mol-1"),
    ("G", 6.67430e-11, 0.00015e-11, "m3.kg-1.s-2"),
    ("EPS_0", 8.8541878188e-12, 0.0000000014e-12, "F/m"),
    ("MU_0", 1.25663706127e-6, 0.00000000020e-6, "N.A-2"),
    ("ALPHA", 7.2973525643e-3, 0.0000000011e-3, ""),
    ("M_E", 9.1093837139e-31, 0.0000000028e-31, "kg"),
    ("M_P", 1.67262192595e-27, 0.00000000052e-27, "kg"),
    ("M_N", 1.67492750056e-27, 0.00000000085e-27, "kg"),
    ("M_U", 1.66053906892e-27, 0.00000000052e-27, "kg"),
    ("RYDBERG", 10973731.568157, 0.000012, "m-1"),
    ("A_0", 5.29177210544e-11, 0.00000000082e-11, "m"),
    ("MU_B", 9.2740100657e-24, 0.0000000029e-24, "J/T"),
    ("MU_N", 5.0507837393e-27, 0.0000000016e-27, "J/T"),
    ("HA", 4.3597447222060e-18, 0.0000000000048e-18, "J"),
    ("L_p", 1.616255e-35, 0.000018e-35, "m"),
    ("M_p", 2.176434e-8, 0.000024e-8, "kg"),
    ("t_p", 5.391247e-44, 0.000060e-44, "s"),
    ("T_p", 1.416784e32, 0.000016e32, "K"),
    ("M_C12", 12.0000000126e-3, 0.0000000037e-3, "kg/mol"),
    ("M_W_S_M_Z", 0.88145, 0.00013, ""),
    ("G_0", 9.80665, 0, "m.s-2"),
    ("ATM", 101325, 0, "Pa"),
]


@pytest.mark.parametrize(("nom", "valeur", "incertitude", "unite"), CODATA_2022)
def test_constante_conforme_a_codata_2022(nom, valeur, incertitude, unite):
    g = getattr(cst, nom)
    assert isinstance(g, Grandeur)
    assert g.unite == unit(unite)
    assert g.valeur == pytest.approx(valeur, rel=1e-12)
    assert g.incertitude == pytest.approx(incertitude, rel=1e-6)


@pytest.mark.parametrize(
    ("nom", "attendu"),
    [
        ("HBAR", 6.62607015e-34 / (2 * math.pi)),
        ("R_GP", 1.380649e-23 * 6.02214076e23),
        ("F", 6.02214076e23 * 1.602176634e-19),
        ("K_J", 2 * 1.602176634e-19 / 6.62607015e-34),
        ("R_K", 6.62607015e-34 / 1.602176634e-19**2),
        ("G_CONDUCTANCE", 2 * 1.602176634e-19**2 / 6.62607015e-34),
        ("PHI_0", 6.62607015e-34 / (2 * 1.602176634e-19)),
    ],
)
def test_constantes_deduites_exactes(nom, attendu):
    g = getattr(cst, nom)
    assert g.incertitude == 0
    assert g.valeur == pytest.approx(attendu, rel=1e-15)


class TestValeursCorrigees:
    """Valeurs fausses de l'ancien paquet constantes (AUDIT.md)."""

    @pytest.mark.parametrize(
        ("nom", "valeur", "unite"),
        [
            ("INCH", 0.0254, "m"),
            ("FOOT", 0.3048, "m"),
            ("YARD", 0.9144, "m"),
            ("MILE", 1609.344, "m"),
            ("GAL_US", 3.785411784e-3, "m3"),
            ("T0", 273.15, "K"),
            ("R_moon", 1.7374e6, "m"),
            ("K_CD", 683, "lm/W"),
            ("NU_CD", 540e12, "Hz"),
            ("OE", 1000 / (4 * math.pi), "A/m"),
        ],
    )
    def test_valeur(self, nom, valeur, unite):
        g = getattr(cst, nom)
        assert g.unite == unit(unite)
        assert g.valeur == pytest.approx(valeur, rel=1e-12)

    def test_temperature_de_planck_avec_la_masse_de_planck(self):
        calcul = (cst.M_p * cst.C**2 / cst.KB).vers("K")
        assert calcul.valeur == pytest.approx(cst.T_p.valeur, rel=1e-5)

    def test_magneton_nucleaire_avec_la_masse_du_proton(self):
        calcul = (cst.E * cst.HBAR / (2 * cst.M_P)).vers("J/T")
        assert calcul.valeur == pytest.approx(cst.MU_N.valeur, rel=1e-9)

    def test_candela(self):
        assert (cst.CD * cst.K_CD).vers("cd").valeur == pytest.approx(1)


class TestNomsSansMasquage:
    def test_g0_est_la_pesanteur(self):
        assert cst.G_0.unite == unit("m.s-2")
        assert cst.G_CONDUCTANCE.unite == unit("S")

    def test_ha_est_l_energie_de_hartree(self):
        assert cst.HA.unite == unit("J")
        assert cst.HECTARE.valeur == 1e4

    def test_gal_est_l_unite_cgs(self):
        assert cst.GAL.unite == unit("m.s-2")
        assert cst.GAL_US.unite == unit("m3")

    def test_chaque_nom_public_a_une_fiche(self):
        constantes = set(cst.__all__) - {"FICHES", "Fiche", "codata", "decrire"}
        assert constantes == set(cst.FICHES)

    @pytest.mark.parametrize("nom", ["NA", "H", "HBAR", "E", "C", "EPS_0", "M_E", "R_GP"])
    def test_noms_des_corriges_existants(self, nom):
        assert isinstance(getattr(cst, nom), Grandeur)


class TestAstronomie:
    @pytest.mark.parametrize(
        ("nom", "valeur"),
        [
            ("R_sun", 6.957e8),
            ("L_sun", 3.828e26),
            ("S_sun", 1361),
            ("T_sun", 5772),
            ("GM_sun", 1.3271244e20),
            ("GM_earth", 3.986004e14),
            ("UA", 149597870700),
        ],
    )
    def test_valeurs_nominales_uai(self, nom, valeur):
        assert getattr(cst, nom).valeur == valeur

    def test_masses_deduites_de_gm_et_g(self):
        assert cst.M_sun.valeur == pytest.approx(1.98841e30, rel=1e-5)
        assert cst.M_earth.valeur == pytest.approx(5.9722e24, rel=1e-4)
        assert cst.M_moon.valeur == pytest.approx(7.346e22, rel=1e-3)
        assert cst.M_sun.incertitude > 0

    def test_parsec_et_annee_lumiere(self):
        assert cst.PC.vers("ly").valeur == pytest.approx(3.26156, rel=1e-5)
        assert cst.AL.valeur == 9460730472580800


def test_charge_de_planck():
    assert cst.Q_p.valeur == pytest.approx(1.875546e-18, rel=1e-6)


def test_g_f_en_unites_si():
    assert cst.G_F.unite == unit("J.m3")
    assert cst.G_F.valeur == pytest.approx(1.4358510e-62, rel=1e-6)


def test_codata_donne_toute_constante_de_scipy():
    rapport = cst.codata("proton-electron mass ratio")
    assert rapport.valeur == pytest.approx(1836.152673426)
    assert rapport.incertitude > 0


def test_toutes_les_cles_de_scipy_lisibles():
    from scipy.constants import physical_constants

    for cle in physical_constants:
        cst.codata(cle)


def test_decrire_cite_la_source():
    assert "CODATA 2022" in cst.decrire("G")
    assert "UAI 2015" in cst.decrire("R_sun")


def test_incertitudes_independantes_mais_etiquetees():
    assert set(cst.G.magnitude.error_components()) != set()
