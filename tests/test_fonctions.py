import math

import numpy as np
import pytest
from pint import DimensionalityError
from uncertainties import ufloat

from grandeurs import grandeur, unit
from grandeurs.fonctions import acos, asin, atan, cos, exp, ln, log10, sin, sqrt, tan


def test_racine_d_une_grandeur_incertaine():
    r = sqrt(grandeur("4.0 m2"))
    assert r.unite == unit("m")
    assert (r.valeur, r.incertitude) == pytest.approx((2.0, 0.025))


def test_sinus_d_un_angle_en_degres():
    s = sin(grandeur("30.0 °"))
    assert s.valeur == pytest.approx(0.5)
    assert s.incertitude == pytest.approx(math.cos(math.pi / 6) * math.radians(0.1))


def test_arc_sinus_rend_des_radians():
    a = asin(0.5)
    assert a == pytest.approx(math.pi / 6)
    assert asin(grandeur(0.5, "")).unite == unit("rad")


def test_fonction_d_un_ufloat():
    assert exp(ufloat(0, 0.1)).std_dev == pytest.approx(0.1)


def test_fonction_d_un_tableau():
    assert list(sqrt(np.array([4.0, 9.0]))) == [2.0, 3.0]


def test_fonction_d_un_tableau_incertain():
    g = grandeur([1.0, 4.0], "m2", incertitude=0.1)
    assert list(sqrt(g).incertitude) == pytest.approx([0.05, 0.025])


def test_exponentielle_d_un_rapport_sans_dimension():
    assert exp(grandeur(1, "m") / grandeur(1, "km")).valeur == pytest.approx(math.exp(1e-3))


def test_exponentielle_d_une_longueur_refusee():
    with pytest.raises(DimensionalityError):
        exp(grandeur(1, "m"))


@pytest.mark.parametrize(
    ("fonction", "x", "attendu"),
    [
        (cos, 0.0, 1.0),
        (tan, math.pi / 4, 1.0),
        (acos, 1.0, 0.0),
        (atan, 1.0, math.pi / 4),
        (ln, math.e, 1.0),
        (log10, 1000.0, 3.0),
    ],
)
def test_valeurs_usuelles(fonction, x, attendu):
    assert fonction(x) == pytest.approx(attendu)
