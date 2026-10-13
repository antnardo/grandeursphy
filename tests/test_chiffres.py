import numpy as np
import pytest
from uncertainties import UFloat, ufloat

from grandeurs import NombreArrondi, arrondir, lire_nombre, reglages_temporaires
from grandeurs.chiffres import FormeNommee, arrondir_valeur, separer_forme_nommee


@pytest.mark.parametrize(
    ("texte", "valeur", "incertitude", "reste"),
    [
        ("1.20 m.s-1", 1.20, 0.01, "m.s-1"),
        ("1200", 1200, 1, ""),
        ("1.2e3 m", 1200, 100, "m"),
        ("1.20(3) m", 1.20, 0.03, "m"),
        ("1.20(3)e3 m", 1200, 30, "m"),
        ("1.20 ± 0.03 m", 1.20, 0.015, "m"),
        ("1.20+/-0.03", 1.20, 0.015, ""),
        ("(1.20 ± 0.03)e3 m", 1200, 15, "m"),
        ("1.20e3 ± 30 g", 1200, 15, "g"),
        ("1,20 m", 1.20, 0.01, "m"),
        ("1.20×10^3 m", 1200, 10, "m"),
        ("1.20 × 10⁻³ m", 1.20e-3, 1e-5, "m"),
        ("1.20x10^{-3}", 1.20e-3, 1e-5, ""),
        ("1.20×10³ m", 1200, 10, "m"),
        ("-0.5 K", -0.5, 0.1, "K"),
        ("12 g.mol-1", 12, 1, "g.mol-1"),
    ],
)
def test_lire_nombre_donne_valeur_incertitude_et_unite(texte, valeur, incertitude, reste):
    lu, suite = lire_nombre(texte)
    assert lu.nominal_value == pytest.approx(valeur)
    assert lu.std_dev == pytest.approx(incertitude)
    assert suite == reste


def test_lire_nombre_sans_chiffres_significatifs_donne_un_flottant_exact():
    lu, _ = lire_nombre("1.20 m", chiffres_significatifs=False)
    assert not isinstance(lu, UFloat)
    assert lu == 1.2


def test_lire_nombre_illisible_leve_value_error():
    with pytest.raises(ValueError, match="aucun nombre"):
        lire_nombre("m.s-1")


@pytest.mark.parametrize(
    ("valeur", "incertitude", "attendu"),
    [
        (1.2, 0.01, "1.20(1)"),
        (1.2345, 0.0096, "1.23(1)"),
        (-1.2345, 0.0096, "-1.23(1)"),
        (1234.5, 12, "1.23(1)e3"),
        (0.000123, 0.000004, "1.23(4)e-4"),
        (12345.678, 0.5, "12345.7(5)"),
        (0.0, 0.02, "0.00(2)"),
    ],
)
def test_arrondir_au_rang_de_l_incertitude(valeur, incertitude, attendu):
    assert arrondir(valeur, incertitude).ecrire() == attendu


def test_arrondir_deux_chiffres_sur_l_incertitude():
    assert arrondir(1234.5, 12, chiffres_incertitude=2).ecrire() == "1235(12)"


@pytest.mark.parametrize(
    ("valeur", "chiffres", "attendu"),
    [(2.675, 3, "2.68"), (9.96, 2, "10"), (8314.46261815324, 4, "8314"), (0.0, 3, "0.00")],
)
def test_arrondir_a_n_chiffres_significatifs_au_plus_proche(valeur, chiffres, attendu):
    assert arrondir(valeur, chiffres=chiffres).ecrire() == attendu


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        (299792458.0, "2.99792458e8"),
        (6.02214076e23, "6.02214076e23"),
        (1200.0, "1200"),
        (0.1 + 0.2, "0.3"),
        (999.9999999999999, "1000"),
        (1e-7, "1e-7"),
    ],
)
def test_valeur_exacte_ecrite_sans_bruit_de_conversion(valeur, attendu):
    assert arrondir(valeur).ecrire() == attendu


def test_nombre_arrondi_porte_ses_chiffres_significatifs():
    assert arrondir(1.2, 0.01) == NombreArrondi(False, "120", -2, 1)
    assert arrondir(1.2, 0.01).nombre_chiffres == 3


@pytest.mark.parametrize(
    ("options", "attendu"),
    [
        ({"incertitude": None}, "1.23e3"),
        ({"notation": "fixe"}, "1230(10)"),
        ({"notation": "ingenieur"}, "1.23(1)e3"),
        ({"decimale": ","}, "1,23(1)e3"),
    ],
)
def test_ecrire_selon_les_options(options, attendu):
    assert arrondir(1234.5, 12).ecrire(**options) == attendu


def test_ecrire_ingenieur_met_l_exposant_multiple_de_trois():
    assert arrondir(0.000123, 0.000004).ecrire(notation="ingenieur") == "123(4)e-6"


def test_valeur_non_finie_ecrite_telle_quelle():
    assert arrondir(float("-inf")).ecrire() == "-inf"


class TestArrondirValeur:
    def test_valeur_exacte_au_reglage_chiffres(self):
        assert arrondir_valeur(9.79828445167129).ecrire() == "9.80"
        with reglages_temporaires(chiffres=5):
            assert arrondir_valeur(9.79828445167129).ecrire() == "9.7983"

    def test_valeur_incertaine_arrondie_d_apres_l_incertitude(self):
        assert arrondir_valeur(ufloat(9.79828, 0.02)).ecrire() == "9.80(2)"
        with reglages_temporaires(chiffres=5):
            assert arrondir_valeur(ufloat(9.79828, 0.02)).ecrire() == "9.80(2)"

    def test_chiffres_explicite_masque_l_incertitude(self):
        assert arrondir_valeur(ufloat(9.79828, 0.02), chiffres=2).ecrire() == "9.8"

    def test_nombre_numpy_accepte(self):
        assert arrondir_valeur(np.float64(2.0)).ecrire() == "2.00"


# Incertitude élargie : « ± » porte k·u, les parenthèses u.


def test_ecrire_pm_sur_l_incertitude_elargie():
    assert arrondir(1234.5, 12, facteur=2).ecrire(incertitude="pm") == "(1.23 ± 0.02)e3"
    assert arrondir(1234.5, 12, facteur=2).ecrire() == "(1.23 ± 0.02)e3"


def test_l_elargissement_peut_changer_le_rang():
    # u = 0,06 : 1.23(6) en écriture courte, mais 2u = 0,12 → 1.2 ± 0.1
    assert arrondir_valeur(ufloat(1.234, 0.06)).ecrire() == "1.23(6)"
    assert arrondir_valeur(ufloat(1.234, 0.06), elargie=True).ecrire() == "1.2 ± 0.1"


@pytest.mark.parametrize(
    ("arrondi", "style"),
    [
        (arrondir(1.2, 0.01), "pm"),
        (arrondir(1.2, 0.01, facteur=2), "courte"),
    ],
)
def test_ecrire_refuse_une_incertitude_au_mauvais_sens(arrondi, style):
    with pytest.raises(ValueError, match="incertitude"):
        arrondi.ecrire(incertitude=style)


def test_ecrire_valeur_seule_accepte_tout_arrondi():
    assert arrondir(1.2, 0.01, facteur=2).ecrire(incertitude=None) == "1.20"


@pytest.mark.parametrize(
    ("texte", "incertitude"),
    [
        ("1.20(3)", 0.03),
        ("1.20(3)e3", 30),
        ("1.20", 0.01),
        ("1.20 ± 0.03", 0.015),
        ("1.20 +- 0.03", 0.015),
    ],
)
def test_lecture_parentheses_en_u_et_pm_en_incertitude_elargie(texte, incertitude):
    lu, _ = lire_nombre(texte)
    assert lu.std_dev == pytest.approx(incertitude)


@pytest.mark.parametrize("u", [0.01, 0.015, 0.02, 0.04, 0.3, 2.5, 30.0, 4e-5])
@pytest.mark.parametrize("style", ["pm", "courte"])
def test_aller_retour_ecriture_lecture_rend_le_meme_u(u, style):
    elargie = style == "pm"
    texte = arrondir_valeur(ufloat(1.234, u), elargie=elargie).ecrire()
    lu, _ = lire_nombre(texte)
    attendu, _ = lire_nombre(arrondir_valeur(lu, elargie=elargie).ecrire())
    assert lu.std_dev == pytest.approx(attendu.std_dev)
    # u se retrouve aux arrondis près de l'écriture (un chiffre sur l'incertitude écrite)
    ecart_ecrit = u * (2 if elargie else 1)
    assert lu.std_dev * (2 if elargie else 1) == pytest.approx(ecart_ecrit, rel=0.5)


@pytest.mark.parametrize("u", [0.01, 0.02, 0.05, 0.5, 3.0])
def test_aller_retour_exact_quand_l_ecriture_ne_perd_rien(u):
    texte = arrondir_valeur(ufloat(1.0, u), elargie=True).ecrire()
    lu, _ = lire_nombre(texte)
    assert lu.std_dev == pytest.approx(u)


@pytest.mark.parametrize("k", [1, 2, 3])
def test_facteur_d_elargissement_reglable(k):
    with reglages_temporaires(facteur_elargissement=k):
        texte = arrondir_valeur(ufloat(1.2, 0.01), elargie=True).ecrire()
        assert texte == f"1.20 ± 0.0{k}"
        lu, _ = lire_nombre(texte)
        assert lu.std_dev == pytest.approx(0.01)
        # les parenthèses ne dépendent pas du facteur
        assert arrondir_valeur(ufloat(1.2, 0.01)).ecrire() == "1.20(1)"
        assert lire_nombre("1.20(1)")[0].std_dev == pytest.approx(0.01)


# Styles nommés (« u(x) = », « U(x) = ») et k à l'appel.


@pytest.mark.parametrize(
    ("arrondi", "options", "attendu"),
    [
        (arrondir(1.2, 0.01), {}, "0.01"),
        (arrondir(1.2, 0.01, facteur=2), {"elargie": True}, "0.02"),
        (arrondir(1234.5, 12, facteur=2), {"elargie": True}, "0.02e3"),
        (arrondir(1234.5, 12, facteur=2), {"elargie": True, "notation": "fixe"}, "20"),
        (arrondir(1234.5, 12, facteur=2), {"elargie": True, "decimale": ","}, "0,02e3"),
        (arrondir(0.000123, 0.000004), {"notation": "ingenieur"}, "4e-6"),
        (arrondir(2.0, chiffres=3), {}, "0"),
    ],
)
def test_ecrire_incertitude_seule_au_rang_et_a_l_exposant_de_la_valeur(arrondi, options, attendu):
    assert arrondi.ecrire_incertitude(**options) == attendu


@pytest.mark.parametrize(
    ("arrondi", "elargie"),
    [(arrondir(1.2, 0.01), True), (arrondir(1.2, 0.01, facteur=2), False)],
)
def test_ecrire_incertitude_refuse_le_mauvais_sens(arrondi, elargie):
    with pytest.raises(ValueError, match="incertitude"):
        arrondi.ecrire_incertitude(elargie=elargie)


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        ("x = 1.20 m ; u(x) = 0.04 m", FormeNommee("1.20 m", "0.04 m", False)),
        ("L=1,20 m;U(L)=4 cm", FormeNommee("1,20 m", "4 cm", True)),
        ("x = 0.500 ; u(x) = 0.002", FormeNommee("0.500", "0.002", False)),
        ("x = 1.20 m ; u(y) = 0.04 m", None),
        ("1.20 m", None),
        ("(1.20 ± 0.04) m", None),
    ],
)
def test_separer_forme_nommee(texte, attendu):
    assert separer_forme_nommee(texte) == attendu


def test_k_a_l_appel_l_emporte_sur_le_reglage():
    assert arrondir_valeur(ufloat(1.2, 0.01), elargie=True, k=3).ecrire() == "1.20 ± 0.03"
    with reglages_temporaires(facteur_elargissement=3):
        assert arrondir_valeur(ufloat(1.2, 0.01), elargie=True, k=1).ecrire() == "1.20 ± 0.01"
    # sans élargissement, k ne change rien : l'incertitude-type s'écrit telle quelle
    assert arrondir_valeur(ufloat(1.2, 0.01), k=3).ecrire() == "1.20(1)"


@pytest.mark.parametrize("k", [0, -1, float("inf"), float("nan"), "2", True])
def test_k_invalide_refuse(k):
    with pytest.raises(ValueError, match="facteur"):
        arrondir_valeur(ufloat(1.2, 0.01), elargie=True, k=k)
