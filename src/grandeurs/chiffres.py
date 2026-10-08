"""Chiffres significatifs : lecture d'un nombre écrit, arrondi et écriture.

Lecture. Un nombre écrit porte sa précision : « 1.20 » a trois chiffres
significatifs. On suit la convention de ``uncertainties.ufloat_fromstr``, qui est
aussi celle de l'enseignement français : l'incertitude-type vaut une unité du
dernier chiffre écrit (« 1.20 » donne 1,20 ± 0,01), et les zéros de droite
comptent (« 1200 » a quatre chiffres significatifs ; on écrit « 1.2e3 » pour en
avoir deux). L'ancienne classe ``CS`` ne comptait pas les zéros de droite d'un
entier ; on y renonce, car cette règle n'est ni celle des programmes ni celle
d'``uncertainties``. Sont aussi lues les écritures « 1.20(3) », « 1.20 ± 0.03 »,
« (1.20 ± 0.03)e3 », « 1,20 », « 1.20×10^3 » et « 1.20×10⁻³ ».

Arrondi. L'incertitude est arrondie à ``chiffres_incertitude`` chiffres
significatifs (un par défaut), et la valeur au même rang : c'est l'incertitude
qui fixe les chiffres significatifs de la valeur. Sans incertitude, la valeur
est exacte et s'écrit en entier, à 15 chiffres significatifs au plus (au-delà,
un flottant ne porte que le bruit des conversions), sauf si l'on demande un
nombre de chiffres. L'arrondi se fait en décimal, sur l'écriture
la plus courte du flottant (``repr``), et au plus proche avec le demi vers le
haut : 2,675 s'arrondit à 2,68 comme on l'attend sur le papier, alors que
``round(2.675, 2)`` donne 2,67 à cause de l'écriture binaire.
"""

import math
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Context, Decimal, localcontext
from typing import TypeAlias

from uncertainties import UFloat, ufloat, ufloat_fromstr

from grandeurs.reglages import Notation, StyleIncertitude

__all__ = ["NombreArrondi", "Valeur", "arrondir", "lire_nombre"]

Valeur: TypeAlias = float | UFloat

_CHIFFRES = r"(?:\d+(?:[.,]\d*)?|[.,]\d+)"
_SIGNE = r"[-+−]?"
_EXPOSANT = (
    r"(?:[eE][-+−]?\d+"
    r"|\s*[×x*·⋅]\s*10\s*(?:\^|\*\*)\s*(?:\{\s*[-+−]?\d+\s*\}|\(\s*[-+−]?\d+\s*\)|[-+−]?\d+)"
    r"|\s*[×x*·⋅]\s*10[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)"
)
_PM = r"\s*(?:±|\+/-|\+-)\s*"

_FORMES = (
    # (1.20 ± 0.03)e3
    re.compile(
        rf"\s*\(\s*(?P<v>{_SIGNE}{_CHIFFRES}){_PM}(?P<u>{_CHIFFRES})\s*\)(?P<e>{_EXPOSANT})?"
    ),
    # 1.20(3)e3
    re.compile(rf"\s*(?P<v>{_SIGNE}{_CHIFFRES})\((?P<c>\d+(?:[.,]\d+)?)\)(?P<e>{_EXPOSANT})?"),
    # 1.20e3 ± 0.03e3, 1.20e3
    re.compile(
        rf"\s*(?P<v>{_SIGNE}{_CHIFFRES})(?P<e>{_EXPOSANT})?"
        rf"(?:{_PM}(?P<u>{_CHIFFRES})(?P<eu>{_EXPOSANT})?)?"
    ),
)

_EXPOSANTS_UNICODE = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺−", "0123456789-+-")


def _exposant(texte: str | None) -> str:
    """Ramène toute écriture d'exposant (``e3``, ``×10^3``, ``×10³``) à ``e3``."""
    if not texte:
        return ""
    texte = texte.translate(_EXPOSANTS_UNICODE).strip()
    if texte[0] in "eE":
        return "e" + texte[1:]
    puissance = re.search(r"10\s*(?:\^|\*\*)?\s*[{(]?\s*([-+]?\d+)", texte)
    if puissance is None:  # pragma: no cover - garanti par l'expression régulière
        raise ValueError(texte)
    return "e" + puissance.group(1)


def _decimal(texte: str) -> str:
    return texte.replace(",", ".").replace("−", "-")


def lire_nombre(texte: str, *, chiffres_significatifs: bool = True) -> tuple[Valeur, str]:
    """Lit le nombre en tête de ``texte`` ; rend sa valeur et le reste du texte.

    La valeur est un ``ufloat`` quand le texte porte une précision (toujours si
    ``chiffres_significatifs``, sinon seulement avec une incertitude explicite),
    un ``float`` sinon. Le reste est en général l'unité.

    >>> lire_nombre("1.20 m.s-1")
    (1.2+/-0.01, 'm.s-1')
    """
    for forme in _FORMES:
        lu = forme.match(texte)
        if lu is None:
            continue
        champs = lu.groupdict()
        valeur = _decimal(champs["v"])
        exposant = _exposant(champs.get("e"))
        reste = texte[lu.end() :].strip()
        if champs.get("c") is not None:
            return ufloat_fromstr(f"{valeur}({_decimal(champs['c'])}){exposant}"), reste
        if champs.get("u") is not None:
            incertitude = _decimal(champs["u"])
            if "eu" in champs:  # 1.20e3 ± 0.03e3 : chaque nombre porte son exposant
                ecart = float(incertitude + _exposant(champs.get("eu")))
                return ufloat(float(valeur + exposant), ecart), reste
            return ufloat_fromstr(f"({valeur}+/-{incertitude}){exposant}"), reste
        if chiffres_significatifs:
            return ufloat_fromstr(valeur + exposant), reste
        return float(valeur + exposant), reste
    raise ValueError(f"aucun nombre lisible au début de {texte!r}")


@dataclass(frozen=True, slots=True)
class NombreArrondi:
    """Nombre arrondi, prêt à écrire : ``(-1)^negatif × chiffres × 10^rang``.

    ``chiffres`` est la suite des chiffres significatifs (``"0"`` pour zéro),
    ``rang`` la puissance de dix du dernier, ``incertitude`` l'incertitude en
    unités de ce dernier chiffre (``None`` pour un nombre exact), ``special`` le
    texte d'une valeur non finie (``"nan"``, ``"inf"``).
    """

    negatif: bool
    chiffres: str
    rang: int
    incertitude: int | None = None
    special: str | None = None

    @property
    def exposant(self) -> int:
        """Puissance de dix du premier chiffre significatif."""
        if self.chiffres == "0":
            return self.rang
        return self.rang + len(self.chiffres) - 1

    @property
    def nombre_chiffres(self) -> int:
        """Nombre de chiffres significatifs."""
        return len(self.chiffres)

    def ecrire(
        self,
        *,
        notation: Notation = "auto",
        decimale: str = ".",
        incertitude: StyleIncertitude | None = "courte",
    ) -> str:
        """Écrit le nombre : ``1.20``, ``1.20(1)``, ``(1.20 ± 0.01)e3``…

        ``incertitude`` vaut ``"courte"``, ``"pm"`` ou ``None`` (valeur seule).
        L'exposant s'écrit ``e3``, que siunitx comprend.
        """
        if self.special is not None:
            return ("-" if self.negatif else "") + self.special
        exposant = self._choisir_exposant(notation)
        mantisse = _virgule(self.chiffres, self.rang - exposant)
        signe = "-" if self.negatif else ""
        suffixe = f"e{exposant}" if exposant else ""
        if incertitude is None or self.incertitude is None:
            texte = f"{signe}{mantisse}{suffixe}"
        elif incertitude == "courte":
            # Les chiffres entre parenthèses portent sur les derniers chiffres écrits :
            # si la notation fixe complète la mantisse par des zéros, l'incertitude aussi.
            ecart = str(self.incertitude) + "0" * max(0, self.rang - exposant)
            texte = f"{signe}{mantisse}({ecart}){suffixe}"
        else:
            ecart = _virgule(str(self.incertitude), self.rang - exposant)
            texte = f"{signe}{mantisse} ± {ecart}"
            if suffixe:
                texte = f"({texte}){suffixe}"
        return texte.replace(".", decimale) if decimale != "." else texte

    def _choisir_exposant(self, notation: Notation) -> int:
        """Puissance de dix mise en facteur (0 en notation fixe).

        En ``"auto"``, la notation fixe est gardée tant que le dernier chiffre
        significatif est au rang des unités ou après (sinon « 1200 » laisserait
        croire à quatre chiffres) et que l'ordre de grandeur reste lisible
        (de 10⁻³ à 10⁶ exclu).
        """
        e = self.exposant
        if notation == "fixe":
            return 0
        if notation == "scientifique":
            return e
        if notation == "ingenieur":
            e3 = 3 * math.floor(e / 3)
            return e3 if self.rang <= e3 else e
        return 0 if self.rang <= 0 and -3 <= e < 6 else e


def _virgule(chiffres: str, decalage: int) -> str:
    """Place la virgule : ``chiffres × 10^decalage`` écrit en notation fixe."""
    if decalage >= 0:
        return chiffres + "0" * decalage
    n = -decalage
    complet = chiffres.rjust(n + 1, "0")
    return f"{complet[:-n]}.{complet[-n:]}"


_CONTEXTE = Context(prec=80)
_CHIFFRES_FLOTTANT = 17  # chiffres décimaux qu'un flottant double peut porter
_CHIFFRES_EXACTS = 15  # au-delà, le bruit des conversions (999.9999999999999)


def _quantifier(nombre: Decimal, rang: int) -> Decimal:
    with localcontext(_CONTEXTE):
        return nombre.quantize(Decimal(1).scaleb(rang), rounding=ROUND_HALF_UP)


def _rang_chiffres(nombre: Decimal, chiffres: int) -> int:
    """Rang du dernier chiffre quand on garde ``chiffres`` chiffres significatifs.

    Un arrondi qui ajoute un chiffre (9,96 → 10,0) remonte le rang d'un cran.
    """
    rang = nombre.adjusted() - (chiffres - 1)
    if _quantifier(nombre, rang).adjusted() > nombre.adjusted():
        rang += 1
    return rang


def _en_decimal(valeur: float) -> Decimal:
    return Decimal(repr(float(valeur)))


def _construire(valeur: Decimal, rang: int, incertitude: int | None) -> NombreArrondi:
    arrondi = _quantifier(valeur, rang)
    signe, chiffres, _ = arrondi.as_tuple()
    texte = "".join(str(c) for c in chiffres).lstrip("0") or "0"
    return NombreArrondi(bool(signe) and texte != "0", texte, rang, incertitude)


def arrondir(
    valeur: float,
    incertitude: float = 0.0,
    *,
    chiffres_incertitude: int = 1,
    chiffres: int | None = None,
) -> NombreArrondi:
    """Arrondit ``valeur`` d'après son incertitude, ou à ``chiffres`` significatifs.

    Sans incertitude ni ``chiffres``, la valeur est exacte et s'écrit avec au
    plus 15 chiffres significatifs (299792458, 6.02214076e23) : les deux derniers
    chiffres d'un flottant double ne portent que le bruit des conversions, et
    1 mol/L s'écrit 1000 mol/m³ plutôt que 999.9999999999999 mol/m³.
    """
    if not math.isfinite(valeur):
        return NombreArrondi(valeur < 0, "0", 0, special=str(abs(valeur)))
    nombre = _en_decimal(valeur)
    if incertitude and math.isfinite(incertitude) and incertitude > 0:
        ecart = _en_decimal(incertitude)
        rang = _rang_chiffres(ecart, chiffres_incertitude)
        if nombre:  # au-delà de 17 chiffres, le flottant n'en porte plus
            rang = max(rang, nombre.adjusted() - _CHIFFRES_FLOTTANT + 1)
        unites = int(_quantifier(ecart, rang).scaleb(-rang))
        return _construire(nombre, rang, unites)
    if chiffres is not None:
        if chiffres < 1:
            raise ValueError("il faut au moins un chiffre significatif")
        rang = _rang_chiffres(nombre, chiffres) if nombre else 1 - chiffres
        return _construire(nombre, rang, None)
    exact = Decimal(format(float(valeur), f".{_CHIFFRES_EXACTS}g"))
    reduit = exact.normalize(_CONTEXTE)
    rang = int(reduit.as_tuple().exponent)
    if rang > 0 and reduit.adjusted() < 6:  # entier exact : 1200, pas 1.2e3
        rang = 0
    return _construire(exact, rang, None)
