"""Grandeurs physiques avec unités, incertitudes et sortie siunitx, au-dessus de pint.

L'API publique est réexportée ici ; les constantes sont dans
:mod:`grandeurs.constantes` (en grandeurs) et :mod:`grandeurs.flottants` (en
flottants SI), les fonctions usuelles qui propagent les incertitudes dans
:mod:`grandeurs.fonctions`.
"""

from grandeurs.angles import DMS, dms, ecrire_angle, lire_angle, ramener
from grandeurs.chiffres import NombreArrondi, arrondir, lire_nombre
from grandeurs.grandeur import Grandeur
from grandeurs.latex import num, qty, unite_siunitx
from grandeurs.registre import ureg
from grandeurs.reglages import (
    Reglages,
    SansUniteError,
    SansUniteWarning,
    configurer,
    reglages,
    reglages_temporaires,
)
from grandeurs.saisie import grandeur, unit
from grandeurs.unites import Unite

__all__ = [
    "DMS",
    "Grandeur",
    "NombreArrondi",
    "Reglages",
    "SansUniteError",
    "SansUniteWarning",
    "Unite",
    "arrondir",
    "configurer",
    "dms",
    "ecrire_angle",
    "grandeur",
    "lire_angle",
    "lire_nombre",
    "num",
    "qty",
    "ramener",
    "reglages",
    "reglages_temporaires",
    "unit",
    "unite_siunitx",
    "ureg",
]
