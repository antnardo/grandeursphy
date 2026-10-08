import pickle

import pint
import pytest

from grandeurs import Grandeur, ureg
from grandeurs.registre import Registre


def test_registre_unique_est_le_registre_d_application():
    assert pint.get_application_registry().get() is ureg
    assert isinstance(ureg, Registre)


def test_quantites_du_registre_sont_des_grandeurs():
    assert isinstance(ureg.Quantity(1, "m"), Grandeur)


@pytest.mark.parametrize(
    ("notation", "nom"),
    [
        ("m.s-1", "meter / second"),
        ("kg.m.s^(-2)", "kilogram * meter / second ** 2"),
        ("mol.L-1", "mole / liter"),
        ("J.mol-1.K-1", "joule / kelvin / mole"),
        ("µm", "micrometer"),
        ("°C", "degree_Celsius"),
        ("L", "liter"),
        ("mL", "milliliter"),
        ("Ω", "ohm"),
        ("Ω", "ohm"),
    ],
)
def test_notations_lues_par_pint(notation, nom):
    assert ureg.parse_units(notation) == ureg.parse_units(nom)


@pytest.mark.parametrize(
    ("nom", "unite"),
    [("j", "day"), ("an", "year"), ("tr", "turn"), ("Torr", "torr")],
)
def test_noms_francais_ajoutes(nom, unite):
    assert ureg.parse_units(nom) == ureg.parse_units(unite)


def test_conversion_avec_notation_de_manuel():
    assert ureg.Quantity(36, "km.h-1").to("m.s-1").m == pytest.approx(10)


def test_tours_par_minute():
    assert ureg.Quantity(60, "tr/min").to("rad/s").m == pytest.approx(6.283185307179586)


def test_grandeur_se_picke():
    g = ureg.Quantity(1.5, "m/s")
    assert pickle.loads(pickle.dumps(g)) == g
