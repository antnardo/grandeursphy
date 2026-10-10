"""Fabrique des constantes : fiche (description, source), lecture de CODATA, registre commun.

Chaque constante publique de :mod:`grandeurs.constantes` et de ses sous-modules
est créée par l'une des fonctions de ce module, qui l'inscrit dans
:data:`FICHES` avec sa description et sa source ; :func:`decrire` les relit.
"""

from dataclasses import dataclass
from typing import Any

import scipy
from scipy.constants import physical_constants
from uncertainties import ufloat

from grandeurs.grandeur import Grandeur
from grandeurs.registre import ureg

__all__ = [
    "CGS",
    "CODATA",
    "FICHES",
    "SI_AUTRES",
    "SI_EXACT",
    "SI_USAGE",
    "UAI_2015_B3",
    "US",
    "Fiche",
    "cles_codata",
    "codata",
    "codata_notee",
    "decrire",
    "deduite",
    "exacte",
    "mesuree",
]

_version = tuple(int(n) for n in scipy.__version__.split(".")[:2])
if _version < (1, 15):  # pragma: no cover - dépend de l'environnement
    raise ImportError(
        f"grandeurs.constantes exige scipy ≥ 1.15 (CODATA 2022) ; scipy {scipy.__version__} "
        "fournit CODATA 2018 et donnerait d'autres valeurs. Mettre scipy à jour : "
        'python -m pip install "scipy>=1.15"'
    )


@dataclass(frozen=True, slots=True)
class Fiche:
    """Ce qu'on sait d'une constante : description, source et valeur."""

    nom: str
    description: str
    source: str
    grandeur: Grandeur


FICHES: dict[str, Fiche] = {}

CODATA = "CODATA 2022, par scipy.constants"
SI_EXACT = "SI, brochure du BIPM, 9e édition (2019) : valeur exacte par définition"
SI_USAGE = "brochure SI du BIPM, 9e édition (2019), tableau 8 : unité en usage avec le SI"
SI_AUTRES = "brochure SI du BIPM, 8e édition (2006), tableau 8 : autre unité hors SI"
CGS = "brochure SI du BIPM, 8e édition (2006), tableau 9 : unité CGS"
US = "accord international de 1959 sur le yard et la livre ; NIST Handbook 44, annexe C"
UAI_2015_B3 = "UAI 2015, résolution B3 : valeur nominale (exacte par convention)"


def _noter(nom: str, valeur: Grandeur, description: str, source: str) -> Grandeur:
    if nom in FICHES:
        raise ValueError(f"constante {nom} définie deux fois")
    FICHES[nom] = Fiche(nom, description, source, valeur)
    return valeur


def codata(cle: str) -> Grandeur:
    """Constante CODATA de scipy, sous la clé anglaise de scipy, en grandeur.

    >>> print(codata("proton-electron mass ratio"))
    1836.15267343 ± 0.00000003
    """
    valeur, unite, incertitude = physical_constants[cle]
    magnitude = ufloat(valeur, incertitude, tag=cle) if incertitude else valeur
    return ureg.Quantity(magnitude, unite)  # type: ignore[no-any-return]


def cles_codata(motif: str = "") -> list[str]:
    """Clés de scipy que :func:`codata` accepte, celles qui contiennent ``motif`` si donné.

    >>> cles_codata("Thomson")
    ['Thomson cross section']
    """
    bas = motif.lower()
    return sorted(cle for cle in physical_constants if bas in cle.lower())


def codata_notee(nom: str, cle: str, description: str) -> Grandeur:
    """Constante CODATA inscrite dans les fiches sous ``nom``."""
    return _noter(nom, codata(cle), description, f"{CODATA}, « {cle} »")


def exacte(nom: str, valeur: float, unite: str, description: str, source: str) -> Grandeur:
    """Constante exacte (par définition ou par convention)."""
    return _noter(nom, ureg.Quantity(valeur, unite), description, source)


def mesuree(
    nom: str, valeur: float, incertitude: float, unite: str, description: str, source: str
) -> Grandeur:
    """Constante mesurée, avec son incertitude-type."""
    grandeur = ureg.Quantity(ufloat(valeur, incertitude, tag=nom), unite)
    return _noter(nom, grandeur, description, source)


def deduite(nom: str, valeur: Any, description: str, source: str) -> Grandeur:
    """Constante calculée d'après d'autres (l'incertitude est propagée)."""
    return _noter(nom, valeur, description, source)


def decrire(nom: str) -> str:
    """Description, valeur et source d'une constante, sur une ligne.

    >>> print(decrire("T0"))
    T0 = 273 K : zéro de l'échelle Celsius (définition de l'échelle Celsius)
    """
    fiche = FICHES[nom]
    return f"{nom} = {fiche.grandeur} : {fiche.description} ({fiche.source})"
