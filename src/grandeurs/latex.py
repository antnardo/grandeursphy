r"""Sortie LaTeX pour siunitx, à appeler depuis pythontex : ``\py{qty(v)}``.

Aucun pont entre pythontex et siunitx n'existe : la pratique consiste à écrire
la commande siunitx depuis Python, ce que font ces fonctions.

- :func:`qty` écrit ``\qty{1.20(1)}{m.s^{-1}}`` (``\SI`` sur demande, pour
  siunitx 2) ; :func:`num` écrit ``\num{1.20(1)}`` ;
- l'incertitude est en notation courte, « 1.20(1) », qui porte
  l'incertitude-type u : siunitx la lit et l'affiche comme le demande son
  option ``uncertainty-mode`` (attention : ``uncertainty-mode=separate`` affiche
  alors « 1.20 ± 0.01 », c'est-à-dire u et non l'incertitude élargie) ;
- la valeur est arrondie au rang de l'incertitude (voir
  :mod:`grandeurs.chiffres`), ou à ``chiffres`` chiffres significatifs (le
  réglage ``chiffres``, 3 par défaut, pour une valeur exacte) ;
- l'exposant s'écrit ``e3`` : siunitx l'affiche « × 10³ » ;
- la virgule décimale est en option (``decimale=","`` ou le réglage
  ``decimale``) ; siunitx lit les deux, et c'est son option
  ``output-decimal-marker`` qui décide de l'affichage ;
- l'unité est littérale, comme dans les documents existants (``kg.m^{-3}``,
  ``\micro m``, ``k\ohm``).

:func:`lire_qty` fait le chemin inverse : ``\qty{1.20(1)}{m.s^{-1}}`` redevient
une grandeur, pour relire une valeur écrite dans un énoncé ou un corrigé.
"""

import re
from typing import Any

import numpy as np
import pint

from grandeurs.affichage import MACROS_SIUNITX
from grandeurs.chiffres import arrondir_valeur
from grandeurs.grandeur import Grandeur
from grandeurs.reglages import Notation, reglages
from grandeurs.saisie import grandeur, unit

__all__ = ["lire_qty", "num", "qty", "unite_siunitx"]

_COMMANDE = re.compile(
    r"\\(?P<macro>qty|SI|num)\s*(?:\[[^\]]*\])?\s*\{(?P<nombre>[^{}]*)\}(?:\s*\{(?P<unite>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\})?"
)
_MACRO_UNITE = re.compile(r"\\(micro|[A-Za-z]+)\s*")
# À l'envers, le premier symbole d'une macro l'emporte (°C plutôt que Δ°C).
_SYMBOLES_SIUNITX: dict[str, str] = {}
for _symbole, _macro in MACROS_SIUNITX.items():
    _SYMBOLES_SIUNITX.setdefault(_macro, _symbole)


def unite_siunitx(unite: Any) -> str:
    r"""Unité en écriture littérale de siunitx : ``"J.mol-1.K-1"`` → ``J.mol^{-1}.K^{-1}``."""
    return unit(unite).ecrire("siunitx")


def _nombre(
    x: Any,
    *,
    incertitude: bool | None,
    chiffres: int | None,
    decimale: str | None,
    notation: Notation | None,
) -> str:
    """Nombre (flottant ou ``ufloat``) écrit pour siunitx, incertitude en notation courte."""
    r = reglages()
    montrer = (r.afficher_incertitude if incertitude is None else incertitude) and chiffres is None
    return arrondir_valeur(x, chiffres).ecrire(
        notation=notation or r.notation,
        decimale=decimale or r.decimale,
        incertitude="courte" if montrer else None,
    )


def num(
    x: Any,
    *,
    incertitude: bool | None = None,
    chiffres: int | None = None,
    decimale: str | None = None,
    notation: Notation | None = None,
) -> str:
    r"""``\num{…}`` d'un nombre, d'un ``ufloat`` ou d'une grandeur sans dimension."""
    if isinstance(x, pint.Quantity):
        if not x.dimensionless:
            raise TypeError(f"{x} a une dimension : utiliser qty()")
        x = x.to("").magnitude
    texte = _nombre(
        x, incertitude=incertitude, chiffres=chiffres, decimale=decimale, notation=notation
    )
    return rf"\num{{{texte}}}"


def qty(
    x: Any,
    unite: Any = None,
    *,
    incertitude: bool | None = None,
    chiffres: int | None = None,
    decimale: str | None = None,
    notation: Notation | None = None,
    macro: str = "qty",
) -> str:
    r"""``\qty{valeur}{unité}`` d'une grandeur, convertie d'abord dans ``unite`` si donnée.

    ``x`` est une grandeur, ou tout ce qu'accepte :func:`grandeurs.grandeur`
    (``qty("1.20 m")``). Un tableau à une dimension donne ``\qtylist``. Une
    grandeur sans unité donne ``\num``. ``macro="SI"`` écrit ``\SI`` (siunitx 2).
    """
    g = x if isinstance(x, pint.Quantity) else grandeur(x)
    if unite is not None:
        g = g.to(unit(unite).pint_unit)

    def ecrire(nombre: Any) -> str:
        return _nombre(
            nombre, incertitude=incertitude, chiffres=chiffres, decimale=decimale, notation=notation
        )

    texte_unite = unit(g).ecrire("siunitx")
    magnitude = g.magnitude
    if np.ndim(magnitude) == 1:
        valeurs = ";".join(ecrire(m) for m in magnitude)
        commande = "qtylist" if texte_unite else "numlist"
        return rf"\{commande}{{{valeurs}}}" + (f"{{{texte_unite}}}" if texte_unite else "")
    if np.ndim(magnitude):
        raise TypeError("qty() écrit un nombre ou une liste, pas un tableau à plusieurs dimensions")
    texte = ecrire(magnitude)
    if not texte_unite:
        return rf"\num{{{texte}}}"
    return rf"\{macro}{{{texte}}}{{{texte_unite}}}"


def _unite_de_siunitx(texte: str) -> str:
    """Unité littérale de siunitx en notation de manuel : ``m.s^{-1}`` → ``m.s^(-1)``."""

    def symbole(macro: re.Match[str]) -> str:
        nom = "\\" + macro.group(1)
        if nom == "\\micro":
            return "µ"
        if nom not in _SYMBOLES_SIUNITX:
            raise ValueError(f"macro siunitx inconnue : {nom}")
        return _SYMBOLES_SIUNITX[nom]

    return _MACRO_UNITE.sub(symbole, texte).replace("^{", "^(").replace("}", ")")


def lire_qty(texte: str) -> Grandeur:
    r"""Lit ``\qty{1.20(1)}{m.s^{-1}}``, ``\SI{…}{…}`` ou ``\num{…}`` ; l'inverse de :func:`qty`.

    Le nombre est lu comme par :func:`grandeurs.grandeur` (incertitude courte,
    qui est l'incertitude-type, virgule, exposant ``e3``) ; un « +- » s'y lit
    comme partout, en incertitude élargie. L'unité littérale de siunitx est
    retraduite (``^{-1}``, ``\micro``, ``\ohm``, ``\degreeCelsius``…).

    >>> print(lire_qty(r"\qty{1,20(1)e3}{kg.m^{-3}}"))
    (1.20 ± 0.02)e3 kg·m⁻³
    """
    lu = _COMMANDE.fullmatch(texte.strip())
    if lu is None or (lu.group("macro") == "num") == (lu.group("unite") is not None):
        raise ValueError(f"commande siunitx illisible : {texte!r}")
    unite = _unite_de_siunitx(lu.group("unite") or "")
    return grandeur(lu.group("nombre").strip(), unite)
