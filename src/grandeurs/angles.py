"""Angles en degrés, minutes et secondes, au-dessus des unités d'angle de pint.

pint convertit déjà entre radians, degrés (``°``), minutes et secondes d'arc
(``arcmin``, ``arcsec``) et tours (``tr``) ; un angle est donc une simple
:class:`grandeurs.Grandeur`. Ce module ajoute ce que pint n'a pas :

- la lecture des écritures sexagésimales : ``lire_angle("30°15'20\\"")`` ;
- l'écriture en degrés-minutes-secondes, avec la retenue juste : l'arrondi
  se fait sur le nombre total de secondes *avant* le découpage, si bien que 30°
  s'écrit 30°00'00" et non 29°59'60" (le défaut de l'ancienne classe
  ``Angle``) ;
- un signe pour l'angle entier : −10°30' vaut −10,5° (l'ancienne classe donnait
  −9,5° pour ``deg=-10, min=30``) ;
- la réduction modulo un tour, dans [0, 360°[ ou ]−180°, 180°].

Un nombre nu passé à ces fonctions est lu en radians, l'unité SI de l'angle
(pint fait de même : le radian vaut 1).
"""

import math
import re
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from grandeurs.grandeur import Grandeur
from grandeurs.registre import ureg

__all__ = ["DMS", "dms", "ecrire_angle", "lire_angle", "ramener"]

_NOMBRE = r"\d+(?:[.,]\d+)?"
_SIGNE = r"^\s*(?P<signe>[-+−]?)\s*"
# 30°15'20" (symboles, chaque terme facultatif) ou 30d15m20s (lettres, degrés exigés :
# « 3 m » seul est une longueur, pas trois minutes d'arc).
_SEXAGESIMAL = (
    re.compile(
        rf"""{_SIGNE}(?:(?P<d>{_NOMBRE})\s*°\s*)?
        (?:(?P<m>{_NOMBRE})\s*['′]\s*)?
        (?:(?P<s>{_NOMBRE})\s*(?:["″]|''|′′)\s*)?$""",
        re.VERBOSE,
    ),
    re.compile(
        rf"{_SIGNE}(?P<d>{_NOMBRE})\s*d\s*(?:(?P<m>{_NOMBRE})\s*m\s*)?(?:(?P<s>{_NOMBRE})\s*s\s*)?$"
    ),
)


def _en_angle(angle: Any) -> Grandeur:
    if isinstance(angle, Grandeur):
        return angle
    return ureg.Quantity(angle, "rad")  # type: ignore[no-any-return]


def dms(degres: float, minutes: float = 0, secondes: float = 0) -> Grandeur:
    """Angle donné en degrés, minutes et secondes, rendu en degrés.

    Le signe du premier terme non nul vaut pour tout l'angle :
    ``dms(-10, 30)`` vaut −10,5° ; ``dms(0, -30)`` vaut −0,5°.
    """
    termes = (degres, minutes, secondes)
    signe = next((math.copysign(1, t) for t in termes if t), 1.0)
    valeur = abs(degres) + abs(minutes) / 60 + abs(secondes) / 3600
    return ureg.Quantity(signe * valeur, "degree")  # type: ignore[no-any-return]


def lire_angle(texte: str) -> Grandeur:
    """Lit un angle écrit : ``"30°15'20\\""``, ``"-10°30'"``, ``"30d15m"``, ``"1.2 rad"``."""
    lu = next((m for forme in _SEXAGESIMAL if (m := forme.match(texte))), None)
    if lu and any(lu.group(n) for n in "dms"):

        def nombre(nom: str) -> float:
            return float((lu.group(nom) or "0").replace(",", "."))

        angle = dms(nombre("d"), nombre("m"), nombre("s"))
        return -angle if lu.group("signe") in ("-", "−") else angle
    angle = ureg.Quantity(texte)
    if not isinstance(angle, Grandeur) or angle.dimensionality:
        raise ValueError(f"angle illisible : {texte!r}")
    return angle


@dataclass(frozen=True, slots=True)
class DMS:
    """Angle découpé en degrés, minutes et secondes, prêt à écrire.

    ``secondes`` est déjà arrondi à ``decimales`` chiffres après la virgule, et
    la retenue est faite : les minutes et les secondes sont toujours < 60.
    """

    negatif: bool
    degres: int
    minutes: int
    secondes: float
    decimales: int = 0

    @classmethod
    def depuis(cls, angle: Any, decimales: int = 0) -> "DMS":
        """Découpe ``angle`` (grandeur d'angle, ou nombre en radians)."""
        degres = float(_en_angle(angle).to("degree").valeur)
        echelle = 10**decimales
        total = round(abs(degres) * 3600 * echelle)  # en 10^-decimales seconde
        d, reste = divmod(total, 3600 * echelle)
        m, s = divmod(reste, 60 * echelle)
        return cls(degres < 0 and total > 0, d, m, s / echelle, decimales)

    @property
    def angle(self) -> Grandeur:
        """L'angle, en degrés."""
        angle = dms(self.degres, self.minutes, self.secondes)
        return -angle if self.negatif else angle

    def _secondes(self, decimale: str) -> str:
        largeur = 2 + (self.decimales + 1 if self.decimales else 0)
        return f"{self.secondes:0{largeur}.{self.decimales}f}".replace(".", decimale)

    def ecrire(self, decimale: str = ".") -> str:
        """Écriture usuelle : ``30°00'00"``."""
        signe = "-" if self.negatif else ""
        return f"{signe}{self.degres}°{self.minutes:02d}'{self._secondes(decimale)}\""

    def latex(self, decimale: str = ".") -> str:
        r"""Écriture siunitx : ``\ang{30;0;0}``."""
        signe = "-" if self.negatif else ""
        secondes = f"{self.secondes:.{self.decimales}f}".replace(".", decimale)
        return rf"\ang{{{signe}{self.degres};{self.minutes};{secondes}}}"

    def __str__(self) -> str:
        return self.ecrire()


def ecrire_angle(
    angle: Any,
    forme: Literal["dms", "dm", "d"] = "dms",
    decimales: int = 0,
    decimale: str = ".",
) -> str:
    """Écrit un angle : ``"dms"`` (30°15'20"), ``"dm"`` (30°15.3') ou ``"d"`` (30.26°).

    ``decimales`` porte sur le dernier terme écrit ; la retenue est faite.
    """
    if forme == "dms":
        return DMS.depuis(angle, decimales).ecrire(decimale)
    degres = float(_en_angle(angle).to("degree").valeur)
    signe = "-" if degres < 0 else ""
    if forme == "d":
        texte = f"{signe}{abs(degres):.{decimales}f}°"
    elif forme == "dm":
        echelle = 10**decimales
        total = round(abs(degres) * 60 * echelle)
        d, m = divmod(total, 60 * echelle)
        largeur = 2 + (decimales + 1 if decimales else 0)
        signe = signe if total else ""
        texte = f"{signe}{d}°{m / echelle:0{largeur}.{decimales}f}'"
    else:
        raise ValueError(f"forme inconnue : {forme!r} (dms, dm ou d)")
    return texte.replace(".", decimale)


def ramener(angle: Any, symetrique: bool = False) -> Grandeur:
    """Ramène un angle dans [0, 360°[ ou, si ``symetrique``, dans ]−180°, 180°].

    Le résultat garde l'unité de l'angle donné, et son incertitude : on retire
    un nombre entier de tours calculé sur la valeur centrale, plutôt que
    d'appliquer ``%``, que ``uncertainties`` déprécie.
    """
    angle = _en_angle(angle)
    tour: Any = ureg.Quantity(1, "turn").to(angle.units)
    reduit: Any = angle - np.floor(angle.valeur / tour.valeur) * tour
    if symetrique:
        reduit = reduit - (reduit.valeur > tour.valeur / 2) * tour
    return reduit  # type: ignore[no-any-return]
