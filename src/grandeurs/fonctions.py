"""Fonctions usuelles (racine, exponentielle, trigonométrie…) qui propagent les incertitudes.

``np.sqrt`` appliqué à une grandeur dont la valeur est un ``ufloat`` échoue :
numpy cherche une méthode ``sqrt`` que ``ufloat`` n'a pas. Les fonctions de ce
module acceptent indifféremment un nombre, un ``ufloat``, un tableau (de
``ufloat`` ou non) et une grandeur, et choisissent la bonne implémentation :
``uncertainties.umath`` pour un ``ufloat``, ``uncertainties.unumpy`` pour un
tableau de ``ufloat``, numpy sinon. Les unités sont vérifiées et converties :
un sinus prend un angle (un nombre nu est en radians), une exponentielle un
nombre sans dimension ; ``asin`` rend des radians, ``sqrt`` la racine de
l'unité.
"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pint
from uncertainties import UFloat, umath, unumpy

__all__ = [
    "acos",
    "asin",
    "atan",
    "cos",
    "exp",
    "ln",
    "log",
    "log10",
    "sin",
    "sqrt",
    "tan",
]


class _FonctionUsuelle:
    """Une fonction mathématique, appliquée selon le type de son argument."""

    def __init__(
        self,
        nom_numpy: str,
        nom_incertain: str,
        entree: str | None,
        sortie: Callable[[Any], Any],
    ) -> None:
        self._numpy = getattr(np, nom_numpy)
        self._umath = getattr(umath, nom_incertain)
        self._unumpy = getattr(unumpy, nom_numpy)
        self._entree = entree
        self._sortie = sortie
        self.__name__ = nom_incertain

    def __call__(self, x: Any) -> Any:
        if not isinstance(x, pint.Quantity):
            return self._appliquer(x)
        entree = x.to(self._entree) if self._entree is not None else x
        resultat = self._appliquer(entree.magnitude)
        return x._REGISTRY.Quantity(resultat, self._sortie(entree.units))

    def _appliquer(self, valeur: Any) -> Any:
        if isinstance(valeur, UFloat):
            return self._umath(valeur)
        if isinstance(valeur, np.ndarray) and valeur.dtype == object:
            return self._unumpy(valeur)
        return self._numpy(valeur)


def _sans_unite(_: Any) -> str:
    return ""


def _radian(_: Any) -> str:
    return "radian"


sqrt = _FonctionUsuelle("sqrt", "sqrt", None, lambda unite: unite**0.5)
exp = _FonctionUsuelle("exp", "exp", "", _sans_unite)
ln = _FonctionUsuelle("log", "log", "", _sans_unite)
log = ln
log10 = _FonctionUsuelle("log10", "log10", "", _sans_unite)
sin = _FonctionUsuelle("sin", "sin", "radian", _sans_unite)
cos = _FonctionUsuelle("cos", "cos", "radian", _sans_unite)
tan = _FonctionUsuelle("tan", "tan", "radian", _sans_unite)
asin = _FonctionUsuelle("arcsin", "asin", "", _radian)
acos = _FonctionUsuelle("arccos", "acos", "", _radian)
atan = _FonctionUsuelle("arctan", "atan", "", _radian)
