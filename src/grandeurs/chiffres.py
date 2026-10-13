"""Chiffres significatifs : lecture d'un nombre écrit, arrondi et écriture.

Lecture. Un nombre écrit porte sa précision : « 1.20 » a trois chiffres
significatifs. On suit la convention de ``uncertainties.ufloat_fromstr``, qui est
aussi celle de l'enseignement français : l'incertitude-type vaut une unité du
dernier chiffre écrit (« 1.20 » donne u = 0,01), et les zéros de droite
comptent (« 1200 » a quatre chiffres significatifs ; on écrit « 1.2e3 » pour en
avoir deux). L'ancienne classe ``CS`` ne comptait pas les zéros de droite d'un
entier ; on y renonce, car cette règle n'est ni celle des programmes ni celle
d'``uncertainties``. Sont aussi lues les écritures « 1.20(3) », « 1.20 ± 0.03 »,
« (1.20 ± 0.03)e3 », « 1,20 », « 1.20×10^3 » et « 1.20×10⁻³ » ; les formes
nommées « x = 1.20 m ; u(x) = 0.03 m » et « x = 1.20 m ; U(x) = 0.06 m » sont
découpées par :func:`separer_forme_nommee`, et c'est :func:`grandeurs.grandeur`
qui les lit, parce qu'elles portent des unités.

Incertitude-type et incertitude élargie. Le paquet calcule avec l'incertitude-type
``u`` (le ``std_dev`` d'``uncertainties``) et écrit l'une ou l'autre comme le
GUM (JCGM 100:2008, 7.2.2 et 7.2.4). La notation parenthésée « 1.20(1) », celle
de la métrologie et de siunitx, et la forme nommée « u(x) = 0.01 » portent
l'incertitude-type : « 1.20(3) » se lit u = 0,03 et u = 0,01 s'écrit « 1.20(1) ».
Ce qui s'écrit derrière un « ± » ou dans « U(x) = 0.02 » est l'incertitude
élargie ``U = k·u``, ``k`` valant le réglage ``facteur_elargissement`` (2 par
défaut) ou l'argument ``k`` de l'appel : u = 0,01 s'écrit « 1.20 ± 0.02 », et
« 1.20 ± 0.03 » se lit u = 0,015, pour que l'écriture se relise.

Arrondi. L'incertitude écrite (``u`` entre parenthèses et après « u(x) = »,
``k·u`` derrière « ± » et après « U(x) = ») est arrondie à ``chiffres_incertitude``
chiffres significatifs (un par défaut), et la valeur au même rang : c'est
l'incertitude qui fixe les chiffres significatifs de la valeur. Les deux
arrondis d'un même nombre n'ont donc pas toujours le même rang : u = 0,06
s'écrit « 1.23(6) » mais « 1.2 ± 0.1 ». Sans incertitude, la valeur est exacte :
:func:`arrondir_valeur`, le point d'arrondi de toutes les écritures du paquet,
l'écrit à ``reglages().chiffres`` chiffres significatifs (3 par défaut) ;
:func:`arrondir`, la fonction de base, l'écrit en entier, à 15 chiffres
significatifs au plus (au-delà, un flottant ne porte que le bruit des
conversions). L'arrondi se fait en décimal, sur l'écriture la plus courte du
flottant (``repr``), et au plus proche avec le demi vers le haut : 2,675
s'arrondit à 2,68 comme on l'attend sur le papier, alors que ``round(2.675, 2)``
donne 2,67 à cause de l'écriture binaire.
"""

import math
import re
from dataclasses import dataclass, replace
from decimal import ROUND_HALF_UP, Context, Decimal, localcontext
from typing import Any, Literal, TypeAlias

from uncertainties import UFloat, ufloat, ufloat_fromstr

from grandeurs.reglages import Notation, StyleIncertitude, reglages, verifier_facteur

__all__ = [
    "FormeNommee",
    "NombreArrondi",
    "Valeur",
    "arrondir",
    "arrondir_valeur",
    "lire_nombre",
    "separer_forme_nommee",
]

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

# x = 1.20 m ; u(x) = 0.03 m, ou U(x) : le même nom des deux côtés, le point-virgule entre.
_FORME_NOMMEE = re.compile(
    r"\s*(?P<nom>[^\s=;()]+)\s*=\s*(?P<v>[^;]+?)\s*;\s*(?P<lettre>[uU])\((?P=nom)\)\s*=\s*(?P<u>.+?)\s*$"
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


@dataclass(frozen=True, slots=True)
class FormeNommee:
    """Les deux membres de « x = 1.20 m ; u(x) = 0.03 m » ; ``elargie`` si la lettre est « U »."""

    valeur: str
    incertitude: str
    elargie: bool


def separer_forme_nommee(texte: str) -> FormeNommee | None:
    """Découpe « x = 1.20 m ; u(x) = 0.03 m » ou « … ; U(x) = 0.06 m » ; ``None`` sinon.

    >>> separer_forme_nommee("L = 1.20 m ; U(L) = 0.04 m")
    FormeNommee(valeur='1.20 m', incertitude='0.04 m', elargie=True)
    >>> separer_forme_nommee("1.20 m") is None
    True
    """
    lu = _FORME_NOMMEE.fullmatch(texte)
    if lu is None:
        return None
    return FormeNommee(lu.group("v"), lu.group("u"), lu.group("lettre") == "U")


def lire_nombre(texte: str, *, chiffres_significatifs: bool = True) -> tuple[Valeur, str]:
    """Lit le nombre en tête de ``texte`` ; rend sa valeur et le reste du texte.

    La valeur est un ``ufloat`` quand le texte porte une précision (toujours si
    ``chiffres_significatifs``, sinon seulement avec une incertitude explicite),
    un ``float`` sinon. Le reste est en général l'unité.

    L'incertitude écrite derrière « ± » est l'incertitude élargie : elle est
    divisée par le réglage ``facteur_elargissement`` (2 par défaut) pour donner
    l'incertitude-type. Celle des parenthèses est l'incertitude-type.

    >>> lire_nombre("1.20 m.s-1")
    (1.2+/-0.01, 'm.s-1')
    >>> lire_nombre("1.20 ± 0.02 m")
    (1.2+/-0.01, 'm')
    >>> lire_nombre("1.20(1) m")
    (1.2+/-0.01, 'm')
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
                elargie = float(incertitude + _exposant(champs.get("eu")))
            else:  # (1.20 ± 0.03)e3 : l'exposant vaut pour les deux
                elargie = float(incertitude + exposant)
            k = reglages().facteur_elargissement
            return ufloat(float(valeur + exposant), elargie / k), reste
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
    texte d'une valeur non finie (``"nan"``, ``"inf"``). ``facteur`` vaut
    ``None`` si ``incertitude`` est l'incertitude-type (écriture courte, style
    « u »), et le facteur d'élargissement ``k`` si c'est l'incertitude élargie
    ``k·u`` (écriture « ± », style « U »).
    """

    negatif: bool
    chiffres: str
    rang: int
    incertitude: int | None = None
    special: str | None = None
    facteur: float | None = None

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
        incertitude: Literal["pm", "courte", "auto"] | None = "auto",
    ) -> str:
        """Écrit le nombre : ``1.20``, ``1.20(1)``, ``(1.20 ± 0.02)e3``…

        ``incertitude`` vaut ``"courte"``, ``"pm"``, ``None`` (valeur seule) ou
        ``"auto"`` : ``"pm"`` si le nombre a été arrondi sur l'incertitude
        élargie (``facteur`` donné), ``"courte"`` sinon. L'écriture doit
        convenir à l'arrondi : « ± » attend l'incertitude élargie, les
        parenthèses l'incertitude-type (sinon ``ValueError``). L'exposant
        s'écrit ``e3``, que siunitx comprend.
        """
        if incertitude == "auto":
            incertitude = "courte" if self.facteur is None else "pm"
        if incertitude is not None and self.incertitude is not None:
            self._verifier_style(incertitude)
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

    def ecrire_incertitude(
        self, *, elargie: bool = False, notation: Notation = "auto", decimale: str = "."
    ) -> str:
        """Écrit l'incertitude seule, au rang et à l'exposant de la valeur : ``0.02``, ``0.02e3``.

        C'est le second membre des styles nommés, « u(x) = 0.01 » (``elargie``
        faux : l'arrondi doit porter sur l'incertitude-type) et « U(x) = 0.02 »
        (``elargie`` vrai : sur l'incertitude élargie), avec la même garde que
        :meth:`ecrire`. Un nombre exact donne ``0``.
        """
        if self.incertitude is None or self.special is not None:
            return "0"
        self._verifier_style("pm" if elargie else "courte")
        exposant = self._choisir_exposant(notation)
        ecart = _virgule(str(self.incertitude), self.rang - exposant)
        texte = f"{ecart}e{exposant}" if exposant else ecart
        return texte.replace(".", decimale) if decimale != "." else texte

    def _verifier_style(self, style: StyleIncertitude) -> None:
        """Refuse d'écrire une incertitude sous une forme qui en changerait le sens."""
        k = reglages().facteur_elargissement
        if style == "courte" and self.facteur not in (None, 1):
            raise ValueError(
                "incertitude élargie : elle s'écrit derrière « ± », les parenthèses "
                "portent l'incertitude-type (arrondir sans facteur)"
            )
        if style == "pm" and self.facteur is None and k != 1:
            raise ValueError(
                f"« ± » porte l'incertitude élargie : arrondir avec facteur={k:g} "
                "(arrondir_valeur(..., elargie=True))"
            )

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
    facteur: float | None = None,
) -> NombreArrondi:
    """Arrondit ``valeur`` d'après son incertitude, ou à ``chiffres`` significatifs.

    ``incertitude`` est l'incertitude-type ; avec ``facteur`` (``k``), l'arrondi
    porte sur l'incertitude élargie ``k × incertitude``, à écrire derrière « ± » ;
    sans, sur l'incertitude-type, à écrire entre parenthèses.

    Sans incertitude ni ``chiffres``, la valeur est exacte et s'écrit avec au
    plus 15 chiffres significatifs (299792458, 6.02214076e23) : les deux derniers
    chiffres d'un flottant double ne portent que le bruit des conversions, et
    1 mol/L s'écrit 1000 mol/m³ plutôt que 999.9999999999999 mol/m³.
    """
    if not math.isfinite(valeur):
        return NombreArrondi(valeur < 0, "0", 0, special=str(abs(valeur)))
    nombre = _en_decimal(valeur)
    if incertitude and math.isfinite(incertitude) and incertitude > 0:
        ecart = _en_decimal(incertitude * (1.0 if facteur is None else facteur))
        rang = _rang_chiffres(ecart, chiffres_incertitude)
        if nombre:  # au-delà de 17 chiffres, le flottant n'en porte plus
            rang = max(rang, nombre.adjusted() - _CHIFFRES_FLOTTANT + 1)
        unites = int(_quantifier(ecart, rang).scaleb(-rang))
        arrondi = _construire(nombre, rang, unites)
        return arrondi if facteur is None else replace(arrondi, facteur=float(facteur))
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


def arrondir_valeur(
    valeur: Any,
    chiffres: int | None = None,
    *,
    elargie: bool = False,
    k: float | None = None,
) -> NombreArrondi:
    """Arrondit un nombre (flottant ou ``ufloat``) comme l'écrivent ``texte`` et ``qty``.

    Une valeur incertaine est arrondie d'après son incertitude : l'incertitude-type
    pour l'écriture courte et le style « u », l'incertitude élargie ``k·u`` pour
    l'écriture « ± » et le style « U » (``elargie=True``, ``k`` valant le réglage
    ``facteur_elargissement`` sauf s'il est donné). Une valeur exacte, ou tout
    nombre si ``chiffres`` est donné, est arrondie à ``chiffres`` chiffres
    significatifs (par défaut le réglage ``chiffres``).

    >>> arrondir_valeur(9.79828445167129).ecrire()
    '9.80'
    >>> arrondir_valeur(ufloat(9.79828, 0.02)).ecrire()
    '9.80(2)'
    >>> arrondir_valeur(ufloat(9.79828, 0.02), elargie=True).ecrire()
    '9.80 ± 0.04'
    >>> arrondir_valeur(ufloat(9.79828, 0.02), elargie=True, k=3).ecrire()
    '9.80 ± 0.06'
    """
    r = reglages()
    facteur = None
    if k is not None:
        k = verifier_facteur(k)
    if elargie:
        facteur = r.facteur_elargissement if k is None else k
    if isinstance(valeur, UFloat):
        centre, incertitude = valeur.nominal_value, valeur.std_dev
    else:
        centre, incertitude = float(valeur), 0.0
    if chiffres is not None:
        incertitude = 0.0
    elif not incertitude:
        chiffres = r.chiffres
    return arrondir(
        centre,
        incertitude,
        chiffres_incertitude=r.chiffres_incertitude,
        chiffres=chiffres,
        facteur=facteur,
    )
