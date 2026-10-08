import math

import pytest

from grandeurs import DMS, dms, ecrire_angle, grandeur, lire_angle, ramener, unit


@pytest.mark.parametrize(
    ("angle", "attendu"),
    [
        (dms(30), "30°00'00\""),
        (grandeur(30, "°").to("rad"), "30°00'00\""),  # pas 29°59'60"
        (grandeur(math.pi / 6, "rad"), "30°00'00\""),
        (dms(12, 59, 59.6), "13°00'00\""),  # retenue en cascade
        (dms(-10, 30), "-10°30'00\""),
        (dms(0, -30), "-0°30'00\""),
    ],
)
def test_ecriture_dms_avec_retenue(angle, attendu):
    assert ecrire_angle(angle) == attendu


def test_signe_pour_tout_l_angle():
    assert dms(-10, 30).valeur == -10.5
    assert dms(0, -30).valeur == -0.5


def test_decimales_sur_les_secondes():
    assert ecrire_angle(dms(30, 15, 20.25), decimales=1, decimale=",") == "30°15'20,2\""


@pytest.mark.parametrize(
    ("texte", "degres"),
    [
        ("30°15'20\"", 30 + 15 / 60 + 20 / 3600),
        ("30° 15′ 20″", 30 + 15 / 60 + 20 / 3600),
        ("-10°30'", -10.5),
        ("30d15m", 30.25),
        ("45°", 45),
        ("12,5°", 12.5),
    ],
)
def test_lire_angle_sexagesimal(texte, degres):
    assert lire_angle(texte).vers("°").valeur == pytest.approx(degres)


def test_lire_angle_dans_une_autre_unite():
    assert lire_angle("1.2 rad").unite == unit("rad")


def test_lire_angle_refuse_une_longueur():
    with pytest.raises(ValueError, match="angle"):
        lire_angle("3 m")


def test_dms_depuis_un_nombre_en_radians():
    assert DMS.depuis(math.pi / 2) == DMS(False, 90, 0, 0.0)


def test_dms_ecrit_en_siunitx():
    assert DMS.depuis(lire_angle("-10°30'")).latex() == r"\ang{-10;30;0}"


def test_dms_rend_l_angle():
    assert DMS.depuis(dms(-10, 30, 15)).angle.valeur == pytest.approx(-10.504166666666666)


@pytest.mark.parametrize(("forme", "attendu"), [("dm", "30°15.3'"), ("d", "30.26°")])
def test_autres_formes(forme, attendu):
    assert ecrire_angle(dms(30, 15, 20), forme, 1 if forme == "dm" else 2) == attendu


def test_forme_inconnue_refusee():
    with pytest.raises(ValueError):
        ecrire_angle(dms(30), "hms")


@pytest.mark.parametrize(
    ("degres", "symetrique", "attendu"),
    [(370, False, 10), (-30, False, 330), (190, True, -170), (180, True, 180), (720, False, 0)],
)
def test_ramener_modulo_un_tour(degres, symetrique, attendu):
    reduit = ramener(grandeur(degres, "°"), symetrique)
    assert reduit.unite == unit("°")
    assert reduit.valeur == pytest.approx(attendu)


def test_ramener_garde_l_unite():
    assert ramener(grandeur(7, "rad")).vers("rad").valeur == pytest.approx(7 - 2 * math.pi)
