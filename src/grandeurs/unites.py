"""Unités comparées physiquement : ``unit("N") == unit("kg.m.s^(-2)")`` vaut ``True``.

Pour pint, ``Unit("N") == Unit("kg*m/s**2")`` est faux : l'égalité des unités y
est l'égalité d'écriture. On ne modifie pas la classe ``Unit`` du registre pour
autant : pint range ses unités dans des caches et des dictionnaires où « N » et
« kg·m·s⁻² » doivent rester distincts (pour les écrire, notamment). On
enveloppe donc l'unité pint dans :class:`Unite`, dont l'égalité est physique,
et dont le seul autre rôle est l'écriture (:meth:`Unite.ecrire`). Pour tout le
reste (dimension, conversion, algèbre), on passe par les grandeurs.

Deux unités sont équivalentes (:func:`equivalentes`) quand elles ont la même
dimension et que la conversion de l'une vers l'autre est l'identité : 0 donne 0
et 1 donne 1. Cette règle unique couvre les unités multiplicatives (facteur 1)
et les unités affines (°C ≠ K, puisque 0 °C donne 273,15 K ; mais un écart de
1 °C vaut 1 K).

Cas limites, conséquences de la définition du SI et non de ce code :

- ``Hz == Bq`` et ``Hz == rad/s`` : le radian est sans dimension, une vitesse
  angulaire a donc la dimension d'une fréquence ;
- ``J == N·m`` : un moment de force a la dimension d'une énergie ;
- ``rad == sr == 1`` ; mais ``° != 1`` (facteur π/180) et ``% != 1``.
"""

import math
from dataclasses import dataclass
from typing import Any

import pint

from grandeurs.affichage import Style, formateur

__all__ = ["Unite", "equivalentes"]


def _unite_pint(unite: Any, registre: Any) -> Any:
    """Ramène une :class:`Unite`, une chaîne ou une unité pint à l'unité pint ; sinon ``None``."""
    if isinstance(unite, Unite):
        return unite.pint_unit
    if isinstance(unite, str):
        return registre.parse_units(unite)
    if isinstance(unite, registre.Unit):
        return unite
    return None


def equivalentes(a: Any, b: Any) -> bool:
    """Égalité physique de deux unités : même dimension et conversion identité (0→0, 1→1).

    ``a`` et ``b`` sont des :class:`Unite`, des unités pint ou des chaînes en
    notation de manuel.

    >>> equivalentes("N", "kg.m.s-2")
    True
    >>> equivalentes("°C", "K")
    False
    """
    registre = pint.get_application_registry()
    ua, ub = _unite_pint(a, registre), _unite_pint(b, registre)
    if ua is None or ub is None:
        raise TypeError(f"pas une unité : {a!r} ou {b!r}")
    if ua.dimensionality != ub.dimensionality:
        return False
    try:
        zero, un = registre.Quantity([0.0, 1.0], ua).to(ub).m
    except Exception:  # pint refuse, par exemple °C vers Δ°C
        return False
    return math.isclose(zero, 0.0, abs_tol=1e-12) and math.isclose(un, 1.0, rel_tol=1e-12)


@dataclass(frozen=True, slots=True, eq=False)
class Unite:
    """Unité pint enveloppée, à égalité physique et écriture française ; voir le module.

    On l'obtient par :func:`grandeurs.unit` ou par ``g.unite``. Elle se compare
    à une autre :class:`Unite`, à une chaîne ou à une unité pint.
    """

    pint_unit: Any

    def __eq__(self, autre: object) -> bool:
        try:
            unite = _unite_pint(autre, self.pint_unit._REGISTRY)
        except Exception:  # chaîne que pint ne lit pas
            return False
        if unite is None:
            return NotImplemented
        return equivalentes(self.pint_unit, unite)

    def __hash__(self) -> int:
        # Deux unités égales ont la même dimension : le hachage n'utilise qu'elle.
        return hash(frozenset(self.pint_unit.dimensionality.items()))

    def ecrire(self, style: Style = "texte") -> str:
        """Écrit l'unité : ``"texte"`` (m·s⁻¹), ``"ascii"`` (m.s-1), ``"siunitx"`` (m.s^{-1})."""
        return formateur(self.pint_unit._REGISTRY).ecrire(self.pint_unit, style)

    def __str__(self) -> str:
        return self.ecrire("texte")

    def __repr__(self) -> str:
        return f"unit({self.ecrire('texte')!r})"
