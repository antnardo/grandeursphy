r"""Sortie LaTeX pour siunitx, à appeler depuis pythontex : ``\py{qty(v)}``.

Aucun pont entre pythontex et siunitx n'existe : la pratique consiste à écrire
la commande siunitx depuis Python, ce que font ces fonctions.

- :func:`qty` écrit ``\qty{1.20(1)}{m.s^{-1}}`` (``\SI`` sur demande, pour
  siunitx 2) ; :func:`num` écrit ``\num{1.20(1)}`` ;
- l'incertitude suit le GUM, comme partout dans le paquet (voir
  :mod:`grandeurs.chiffres`) : en notation courte « 1.20(1) » par défaut
  (``style="courte"``), qui porte l'incertitude-type u et que siunitx affiche
  comme le demande son option ``uncertainty-mode`` ; derrière ``\pm`` avec
  ``style="pm"``, l'incertitude élargie k·u (``\qty{1.20 \pm 0.02}{m}`` ;
  siunitx ne lit l'exposant d'un « ± » qu'en fin de nombre,
  ``1.20 \pm 0.02 e3``) ; nommée avec ``style="u"``
  (``x = \qty{1.20}{m} ; u(x) = \qty{0.01}{m}``) ou ``style="U"``
  (``x = \qty{1.20}{m} ; U(x) = \qty{0.02}{m}``) ;
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
from collections.abc import Callable
from typing import Any, Literal

import numpy as np

from grandeurs.affichage import MACROS_SIUNITX
from grandeurs.chiffres import arrondir_valeur, separer_forme_nommee
from grandeurs.grandeur import Grandeur
from grandeurs.reglages import Notation, StyleIncertitude, reglages
from grandeurs.saisie import grandeur, unit

__all__ = ["lire_qty", "num", "qty", "unite_siunitx"]

_COMMANDE = re.compile(
    r"\\(?P<macro>qty|SI|num)\s*(?:\[[^\]]*\])?\s*\{(?P<nombre>[^{}]*)\}(?:\s*\{(?P<unite>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\})?"
)
_MACRO_UNITE = re.compile(r"\\(micro|[A-Za-z]+)\s*")
# « (1.20 ± 0.02)e3 » à l'écran, « 1.20 \pm 0.02 e3 » pour siunitx, et retour.
_PM_EXPOSANT = re.compile(r"^\((.+) ± (.+)\)(e[-+]?\d+)$")
_PM_EXPOSANT_SIUNITX = re.compile(r"^(.+?) ± (.+?) (e[-+]?\d+)$")
# À l'envers, le premier symbole d'une macro l'emporte (°C plutôt que Δ°C).
_SYMBOLES_SIUNITX: dict[str, str] = {}
for _symbole, _macro in MACROS_SIUNITX.items():
    _SYMBOLES_SIUNITX.setdefault(_macro, _symbole)


def unite_siunitx(unite: Any) -> str:
    r"""Unité en écriture littérale de siunitx : ``"J.mol-1.K-1"`` → ``J.mol^{-1}.K^{-1}``."""
    return unit(unite).ecrire("siunitx")


def _vers_siunitx(nombre: str) -> str:
    r"""« (1.20 ± 0.02)e3 » devient « 1.20 \pm 0.02 e3 », la forme à exposant que siunitx lit."""
    return _PM_EXPOSANT.sub(r"\1 ± \2 \3", nombre).replace("±", r"\pm")


def _de_siunitx(nombre: str) -> str:
    """Le chemin inverse de :func:`_vers_siunitx`, pour :func:`grandeurs.lire_nombre`."""
    return _PM_EXPOSANT_SIUNITX.sub(r"(\1 ± \2)\3", nombre.replace(r"\pm", "±"))


def _commande(magnitude: Any, texte_unite: str, ecrire: Callable[[Any], str], macro: str) -> str:
    r"""``\qty{…}{…}``, ``\num{…}`` ou ``\qtylist`` selon l'unité et la forme de ``magnitude``."""
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


def _ecrire(
    g: Grandeur,
    *,
    incertitude: bool | None,
    chiffres: int | None,
    decimale: str | None,
    notation: Notation | None,
    style: StyleIncertitude,
    nom: str,
    k: float | None,
    macro: str,
) -> str:
    """Commande siunitx d'une grandeur, dans l'un des quatre styles d'incertitude."""
    r = reglages()
    montrer = (r.afficher_incertitude if incertitude is None else incertitude) and chiffres is None
    elargie = montrer and style in ("pm", "U")
    notation = notation or r.notation
    decimale = decimale or r.decimale
    texte_unite = unit(g).ecrire("siunitx")

    def ecrire(m: Any, forme: Literal["pm", "courte"] | None) -> str:
        arrondi = arrondir_valeur(m, chiffres, elargie=elargie, k=k)
        return _vers_siunitx(
            arrondi.ecrire(notation=notation, decimale=decimale, incertitude=forme)
        )

    def ecrire_ecart(m: Any) -> str:
        arrondi = arrondir_valeur(m, chiffres, elargie=elargie, k=k)
        return arrondi.ecrire_incertitude(elargie=elargie, notation=notation, decimale=decimale)

    def commande(ecrire_nombre: Callable[[Any], str]) -> str:
        return _commande(g.magnitude, texte_unite, ecrire_nombre, macro)

    if style in ("u", "U"):
        texte = f"{nom} = {commande(lambda m: ecrire(m, None))}"
        if montrer and np.any(g.incertitude):
            texte += f" ; {style}({nom}) = {commande(ecrire_ecart)}"
        return texte
    forme: Literal["pm", "courte"] | None = None
    if montrer:
        forme = "pm" if style == "pm" else "courte"
    return commande(lambda m: ecrire(m, forme))


def num(
    x: Any,
    *,
    incertitude: bool | None = None,
    chiffres: int | None = None,
    decimale: str | None = None,
    notation: Notation | None = None,
    style: StyleIncertitude = "courte",
    nom: str = "x",
    k: float | None = None,
) -> str:
    r"""``\num{…}`` d'un nombre, d'un ``ufloat`` ou d'une grandeur sans dimension.

    Mêmes options que :func:`qty` : ``style`` (``"courte"`` par défaut,
    ``\num{1.23(1)}`` ; ``"pm"``, ``\num{1.23 \pm 0.02}`` ; ``"u"``,
    ``x = \num{1.23} ; u(x) = \num{0.01}`` ; ``"U"``,
    ``x = \num{1.23} ; U(x) = \num{0.02}``), ``nom`` et ``k``.
    """
    if isinstance(x, Grandeur):
        if not x.dimensionless:
            raise TypeError(f"{x} a une dimension : utiliser qty()")
        x = x.to("").magnitude
    return _ecrire(
        grandeur(x, ""),
        incertitude=incertitude,
        chiffres=chiffres,
        decimale=decimale,
        notation=notation,
        style=style,
        nom=nom,
        k=k,
        macro="num",
    )


def qty(
    x: Any,
    unite: Any = None,
    *,
    incertitude: bool | None = None,
    chiffres: int | None = None,
    decimale: str | None = None,
    notation: Notation | None = None,
    style: StyleIncertitude = "courte",
    nom: str = "x",
    k: float | None = None,
    macro: str = "qty",
) -> str:
    r"""``\qty{valeur}{unité}`` d'une grandeur, convertie d'abord dans ``unite`` si donnée.

    ``x`` est une grandeur, ou tout ce qu'accepte :func:`grandeurs.grandeur`
    (``qty("1.20 m")``). Un tableau à une dimension donne ``\qtylist``. Une
    grandeur sans unité donne ``\num``. ``macro="SI"`` écrit ``\SI`` (siunitx 2).

    L'incertitude est écrite selon ``style`` : ``"courte"`` (par défaut),
    l'incertitude-type entre parenthèses, ``\qty{1.20(1)}{m}`` ; ``"pm"``,
    l'incertitude élargie ``k·u`` derrière ``\pm``, ``\qty{1.20 \pm 0.02}{m}``
    (``k`` : réglage ``facteur_elargissement``, ou l'argument ``k``) ; ``"u"``,
    ``x = \qty{1.20}{m} ; u(x) = \qty{0.01}{m}`` ; ``"U"``,
    ``x = \qty{1.20}{m} ; U(x) = \qty{0.02}{m}`` (le nom par ``nom``).
    """
    g = x if isinstance(x, Grandeur) else grandeur(x)
    if unite is not None:
        g = g.to(unit(unite).pint_unit)
    return _ecrire(
        g,
        incertitude=incertitude,
        chiffres=chiffres,
        decimale=decimale,
        notation=notation,
        style=style,
        nom=nom,
        k=k,
        macro=macro,
    )


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


def _lire_commande(texte: str) -> tuple[str, str]:
    """Nombre (en écriture de :mod:`grandeurs.chiffres`) et unité de manuel d'une commande."""
    lu = _COMMANDE.fullmatch(texte.strip())
    if lu is None or (lu.group("macro") == "num") == (lu.group("unite") is not None):
        raise ValueError(f"commande siunitx illisible : {texte!r}")
    return _de_siunitx(lu.group("nombre").strip()), _unite_de_siunitx(lu.group("unite") or "")


def lire_qty(texte: str) -> Grandeur:
    r"""Lit ``\qty{1.20(1)}{m.s^{-1}}``, ``\SI{…}{…}`` ou ``\num{…}`` ; l'inverse de :func:`qty`.

    Le nombre est lu comme par :func:`grandeurs.grandeur` : l'incertitude courte,
    « 1.20(1) », est l'incertitude-type, celle qui suit ``\pm`` (« ± », « +- »)
    l'incertitude élargie, divisée par ``k`` ; virgule et exposant ``e3`` sont
    lus, y compris ``1.20 \pm 0.02 e3``. Les formes nommées
    ``x = \qty{1.20}{m} ; u(x) = \qty{0.01}{m}`` et ``… ; U(x) = \qty{0.02}{m}``
    sont lues de même. L'unité littérale de siunitx est retraduite (``^{-1}``,
    ``\micro``, ``\ohm``, ``\degreeCelsius``…).

    >>> print(lire_qty(r"\qty{1,20(1)e3}{kg.m^{-3}}"))
    (1.20 ± 0.02)e3 kg·m⁻³
    >>> lire_qty(r"x = \qty{1.20}{m} ; U(x) = \qty{0.04}{m}").incertitude
    0.02
    """
    forme = separer_forme_nommee(texte)
    if forme is None:
        return grandeur(*_lire_commande(texte))
    valeur, unite = _lire_commande(forme.valeur)
    ecart, unite_ecart = _lire_commande(forme.incertitude)
    lettre = "U" if forme.elargie else "u"
    return grandeur(f"x = {valeur} {unite} ; {lettre}(x) = {ecart} {unite_ecart}", unite)
