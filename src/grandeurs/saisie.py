"""Points d'entrée : :func:`grandeur` pour créer une grandeur, :func:`unit` pour une unité.

``grandeur`` accepte toutes les écritures courantes et les ramène à une
:class:`grandeurs.Grandeur` du registre unique. Une valeur sans unité est
acceptée, sans dimension, et l'oubli est signalé selon ``reglages().sans_unite``.
Pour une grandeur réellement sans dimension, on le dit : ``grandeur(0.5, "")``
ou ``grandeur(0.5, "1")`` ne déclenchent rien.
"""

import reprlib
from typing import Any

import numpy as np
import pint
from uncertainties import UFloat, ufloat, unumpy

from grandeurs.chiffres import lire_nombre
from grandeurs.grandeur import Grandeur
from grandeurs.registre import ureg
from grandeurs.reglages import reglages, signaler
from grandeurs.unites import Unite

__all__ = ["grandeur", "unit"]


def unit(unite: Any) -> Unite:
    """Unité à égalité physique : ``unit("N") == unit("kg.m.s^(-2)")`` vaut ``True``.

    ``unite`` est une chaîne (notation de manuel ou de pint), une
    :class:`grandeurs.Unite`, une unité pint ou une grandeur (dont on prend
    l'unité). Sert aussi à écrire une unité (``unit("J/mol.K").ecrire("siunitx")``)
    et à nommer celle d'une conversion (``qty(v, "km/h")``).
    """
    if isinstance(unite, Unite):
        return unite
    if isinstance(unite, pint.Quantity):
        return Unite(unite.units)
    if isinstance(unite, ureg.Unit):
        return Unite(unite)
    if isinstance(unite, str):
        return Unite(ureg.parse_units(unite))
    raise TypeError(f"unité illisible : {unite!r}")


def _unite_pint(unite: Any) -> Any:
    return unit(unite).pint_unit


def _avec_incertitude(valeur: Any, incertitude: Any) -> Any:
    if isinstance(valeur, UFloat) or (isinstance(valeur, np.ndarray) and valeur.dtype == object):
        raise ValueError("la valeur porte déjà une incertitude")
    if np.ndim(valeur) or np.ndim(incertitude):
        valeurs, incertitudes = np.broadcast_arrays(valeur, incertitude)
        return unumpy.uarray(valeurs.astype(float), incertitudes.astype(float))
    return ufloat(float(valeur), float(incertitude))


def grandeur(valeur: Any, unite: Any = None, incertitude: Any = None) -> Grandeur:
    """Crée une grandeur.

    - ``grandeur("1.20 m.s-1")`` : chaîne avec unité ; « 1.20 » a trois
      chiffres significatifs, donc une incertitude de 0,01 (voir
      :mod:`grandeurs.chiffres` pour les écritures lues : « 1.20(3) »,
      « 1.20 ± 0.03 », « 1,20 », « 1.20×10^3 »…) ;
    - ``grandeur(1.2, "m/s")``, ``grandeur(np.array([1, 2]), "m")`` : nombre ou
      tableau, exact sauf ``incertitude`` ;
    - ``grandeur(1.2, "m", incertitude=0.05)`` ou ``incertitude="5 cm"`` ;
    - ``grandeur(q, "km")`` : conversion d'une grandeur ou d'une chaîne qui a
      déjà une unité.

    Sans unité, la grandeur est sans dimension et l'oubli est signalé selon
    ``reglages().sans_unite``.
    """
    unite_lue: Any = None
    if isinstance(valeur, str):
        valeur, texte_unite = lire_nombre(
            valeur, chiffres_significatifs=reglages().chiffres_significatifs
        )
        unite_lue = texte_unite or None
    elif isinstance(valeur, pint.Quantity):
        if valeur._REGISTRY is not ureg:  # quantité d'un autre registre : par le nom long
            valeur = ureg.Quantity(valeur.magnitude, f"{valeur.units:D}")
        valeur, unite_lue = valeur.magnitude, valeur.units

    if unite_lue is None and unite is None:
        signaler(
            reglages().sans_unite,
            f"grandeur {reprlib.repr(valeur)} créée sans unité : elle est sans dimension",
        )
        unite_lue = ""
    elif unite_lue is None:
        unite_lue, unite = unite, None

    if incertitude is not None:
        if isinstance(incertitude, str | pint.Quantity):
            incertitude = grandeur(incertitude).to(_unite_pint(unite_lue)).valeur
        valeur = _avec_incertitude(valeur, incertitude)

    resultat = ureg.Quantity(valeur, _unite_pint(unite_lue))
    if unite is not None:
        resultat = resultat.to(_unite_pint(unite))
    return resultat  # type: ignore[no-any-return]
