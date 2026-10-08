r"""Sortie LaTeX pour siunitx, à appeler depuis pythontex : ``\py{qty(v)}``.

Aucun pont entre pythontex et siunitx n'existe : la pratique consiste à écrire
la commande siunitx depuis Python, ce que font ces fonctions.

- :func:`qty` écrit ``\qty{1.20(1)}{m.s^{-1}}`` (``\SI`` sur demande, pour
  siunitx 2) ; :func:`num` écrit ``\num{1.20(1)}`` ;
- l'incertitude est en notation courte, « 1.20(1) » : siunitx la lit et
  l'affiche comme le demande son option ``uncertainty-mode`` ;
- la valeur est arrondie au rang de l'incertitude (voir
  :mod:`grandeurs.chiffres`), ou à ``chiffres`` chiffres significatifs ;
- l'exposant s'écrit ``e3`` : siunitx l'affiche « × 10³ » ;
- la virgule décimale est en option (``decimale=","`` ou le réglage
  ``decimale``) ; siunitx lit les deux, et c'est son option
  ``output-decimal-marker`` qui décide de l'affichage ;
- l'unité est littérale, comme dans les documents existants (``kg.m^{-3}``,
  ``\micro m``, ``k\ohm``).
"""

from typing import Any

import numpy as np
import pint
from uncertainties import UFloat

from grandeurs.chiffres import arrondir
from grandeurs.reglages import Notation, reglages
from grandeurs.saisie import grandeur, unit

__all__ = ["num", "qty", "unite_siunitx"]


def unite_siunitx(unite: Any) -> str:
    r"""Unité en écriture littérale de siunitx : ``"J.mol-1.K-1"`` → ``J.mol^{-1}.K^{-1}``."""
    return unit(unite).latex()


def _nombre(
    valeur: float,
    incertitude: float,
    *,
    montrer_incertitude: bool | None,
    chiffres: int | None,
    decimale: str | None,
    notation: Notation | None,
) -> str:
    r = reglages()
    montrer = r.afficher_incertitude if montrer_incertitude is None else montrer_incertitude
    nombre = arrondir(
        valeur,
        0.0 if chiffres is not None else incertitude,
        chiffres_incertitude=r.chiffres_incertitude,
        chiffres=chiffres,
    )
    return nombre.ecrire(
        notation=notation or r.notation,
        decimale=decimale or r.decimale,
        incertitude="courte" if montrer and chiffres is None else None,
    )


def _valeur_incertitude(x: Any) -> tuple[float, float]:
    if isinstance(x, UFloat):
        return x.nominal_value, x.std_dev
    return float(x), 0.0


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
    valeur, ecart = _valeur_incertitude(x)
    texte = _nombre(
        valeur,
        ecart,
        montrer_incertitude=incertitude,
        chiffres=chiffres,
        decimale=decimale,
        notation=notation,
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
        valeur, ecart = _valeur_incertitude(nombre)
        return _nombre(
            valeur,
            ecart,
            montrer_incertitude=incertitude,
            chiffres=chiffres,
            decimale=decimale,
            notation=notation,
        )

    texte_unite = unit(g).latex()
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
