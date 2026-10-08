"""Unités comparées physiquement : ``unit("N") == unit("kg.m.s^(-2)")`` vaut ``True``.

Pour pint, ``Unit("N") == Unit("kg*m/s**2")`` est faux : l'égalité des unités y
est l'égalité d'écriture. On ne modifie pas la classe ``Unit`` du registre pour
autant : pint range ses unités dans des caches et des dictionnaires où « N » et
« kg·m·s⁻² » doivent rester distincts (pour les écrire, notamment). On
enveloppe donc l'unité pint dans :class:`Unite`, dont l'égalité est physique.

Deux unités sont égales quand elles ont la même dimension et que la conversion
de l'une vers l'autre est l'identité : 0 donne 0 et 1 donne 1. Cette règle
unique couvre les unités multiplicatives (facteur 1) et les unités affines
(°C ≠ K, puisque 0 °C donne 273,15 K ; mais un écart de 1 °C vaut 1 K).

Cas limites, conséquences de la définition du SI et non de ce code :

- ``Hz == Bq`` et ``Hz == rad/s`` : le radian est sans dimension, une vitesse
  angulaire a donc la dimension d'une fréquence ;
- ``J == N·m`` : un moment de force a la dimension d'une énergie ;
- ``rad == sr == 1`` ; mais ``° != 1`` (facteur π/180) et ``% != 1``.

Pour l'égalité d'écriture, il reste :meth:`Unite.identique`.
"""

import math
from dataclasses import dataclass
from typing import Any

from grandeurs.affichage import Style, formateur
from grandeurs.simplification import simplificateur

__all__ = ["Unite"]


@dataclass(frozen=True, slots=True, eq=False)
class Unite:
    """Unité pint enveloppée, à égalité physique ; voir le module.

    On l'obtient par :func:`grandeurs.unit`. Elle se combine (``*``, ``/``,
    ``**``) avec d'autres unités, des chaînes ou des unités pint, et un nombre
    multiplié par une unité donne une grandeur : ``3 * unit("m")``.
    """

    pint_unit: Any

    # Construction et conversions entre formes

    @property
    def registre(self) -> Any:
        return self.pint_unit._REGISTRY

    def _autre(self, autre: object) -> "Unite | None":
        """Ramène ``autre`` (Unite, chaîne, unité pint) à une Unite, ou ``None``."""
        if isinstance(autre, Unite):
            return autre
        if isinstance(autre, str):
            return Unite(self.registre.parse_units(autre))
        if isinstance(autre, self.registre.Unit):
            return Unite(autre)
        return None

    # Égalité physique

    def __eq__(self, autre: object) -> bool:
        try:
            unite = self._autre(autre)
        except Exception:
            return False
        if unite is None:
            return NotImplemented
        return self.equivalente(unite)

    def __hash__(self) -> int:
        # Deux unités égales ont la même dimension : le hachage n'utilise qu'elle.
        return hash(frozenset(self.pint_unit.dimensionality.items()))

    def equivalente(self, autre: "Unite | str") -> bool:
        """Égalité physique : même dimension et conversion identité (0→0, 1→1)."""
        unite = self._autre(autre)
        if unite is None:
            raise TypeError(f"pas une unité : {autre!r}")
        if self.pint_unit.dimensionality != unite.pint_unit.dimensionality:
            return False
        try:
            zero, un = self.registre.Quantity([0.0, 1.0], self.pint_unit).to(unite.pint_unit).m
        except Exception:  # pint refuse, par exemple °C vers Δ°C
            return False
        return math.isclose(zero, 0.0, abs_tol=1e-12) and math.isclose(un, 1.0, rel_tol=1e-12)

    def identique(self, autre: "Unite | str") -> bool:
        """Égalité d'écriture, celle de pint : N et kg·m·s⁻² diffèrent."""
        unite = self._autre(autre)
        return unite is not None and self.pint_unit == unite.pint_unit

    # Propriétés

    @property
    def dimension(self) -> str:
        """Dimension, dans l'écriture de pint : ``[length] / [time]``."""
        return str(self.pint_unit.dimensionality)

    @property
    def sans_dimension(self) -> bool:
        return bool(self.pint_unit.dimensionless)

    @property
    def affine(self) -> bool:
        """Unité à décalage d'origine (°C, °F), qui ne se multiplie pas librement."""
        return not self.registre.Quantity(1, self.pint_unit)._is_multiplicative

    @property
    def facteur_si(self) -> float:
        """Valeur d'une unité en unités SI cohérentes (km → 1000)."""
        if self.affine:
            return self._en_si(1.0) - self._en_si(0.0)
        return self._en_si(1.0)

    @property
    def decalage_si(self) -> float:
        """Valeur en SI du zéro de l'unité (°C → 273,15 ; 0 pour une unité multiplicative)."""
        return self._en_si(0.0) if self.affine else 0.0

    def _en_si(self, valeur: float) -> float:
        return float(self.registre.Quantity(valeur, self.pint_unit).to_base_units().m)

    def si(self) -> "Unite":
        """Unité SI cohérente simplifiée, avec unités dérivées (kg·m·s⁻² → N)."""
        conteneur = simplificateur(self.registre).unites(self.pint_unit._units)
        return Unite(self.registre.Unit(conteneur))

    # Écriture

    def ecrire(self, style: Style = "texte") -> str:
        """Écrit l'unité : ``"texte"`` (m·s⁻¹), ``"ascii"`` (m.s-1), ``"siunitx"``."""
        return formateur(self.registre).ecrire(self.pint_unit, style)

    def latex(self) -> str:
        """Unité pour siunitx, en écriture littérale : ``m.s^{-1}``."""
        return self.ecrire("siunitx")

    def __str__(self) -> str:
        return self.ecrire("texte")

    def __repr__(self) -> str:
        return f"unit({self.ecrire('texte')!r})"

    # Algèbre

    def __mul__(self, autre: object) -> Any:
        unite = self._algebre(autre)
        if unite is not None:
            return Unite(self.pint_unit * unite.pint_unit)
        return self.registre.Quantity(1, self.pint_unit) * autre

    def __rmul__(self, autre: object) -> Any:
        unite = self._algebre(autre)
        if unite is not None:
            return Unite(unite.pint_unit * self.pint_unit)
        return autre * self.registre.Quantity(1, self.pint_unit)

    def __truediv__(self, autre: object) -> Any:
        unite = self._algebre(autre)
        if unite is not None:
            return Unite(self.pint_unit / unite.pint_unit)
        return self.registre.Quantity(1, self.pint_unit) / autre

    def __rtruediv__(self, autre: object) -> Any:
        unite = self._algebre(autre)
        if unite is not None:
            return Unite(unite.pint_unit / self.pint_unit)
        return autre / self.registre.Quantity(1, self.pint_unit)

    def __pow__(self, puissance: float) -> "Unite":
        return Unite(self.pint_unit**puissance)

    def _algebre(self, autre: object) -> "Unite | None":
        if isinstance(autre, self.registre.Quantity):
            return None
        return self._autre(autre)
