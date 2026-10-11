"""La grandeur physique : une quantité pint, plus incertitude et écriture.

Pourquoi une sous-classe de la ``Quantity`` de pint plutôt qu'une classe à part
qui l'envelopperait : une grandeur *est* alors une quantité pint. Conversions,
unités affines, tableaux numpy, fonctions numpy, contextes, compatibilité avec
les autres bibliothèques qui reconnaissent pint : tout vient sans une ligne de
code, et ce qui suit n'ajoute que ce qui manque à pint. pint prévoit ce mode
d'extension (un registre peut déclarer sa propre classe ``Quantity``).

Ce qui est ajouté :

- les incertitudes : la valeur peut être un ``ufloat`` d'``uncertainties`` (ou
  un tableau de ``ufloat``), que pint transporte tel quel ; ``uncertainties``
  propage les incertitudes au premier ordre, corrélations comprises
  (``a - a`` vaut exactement 0) ;
- l'écriture : valeur arrondie d'après l'incertitude, unités à la française
  (:meth:`texte`, ``str``), sortie siunitx (:meth:`latex`) ; derrière « ± »
  s'écrit l'incertitude élargie (2u par défaut), entre parenthèses
  l'incertitude-type u ;
- la simplification en SI avec unités dérivées (:meth:`si`) et la conversion
  dans une unité écrite comme dans un manuel (:meth:`vers`) ;
- les opérations qu'``uncertainties`` déprécie sur ses nombres : les
  comparaisons d'ordre portent sur les valeurs centrales, ``abs`` change le
  signe des valeurs centrales négatives, ``round`` refuse une grandeur
  incertaine.

Les règles de pint restent entières : ``longueur + 2`` est refusé, 1 m n'est
pas le nombre 1, deux dimensions incompatibles ne s'additionnent pas.
"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pint
from uncertainties import UFloat, unumpy

from grandeurs.chiffres import NombreArrondi, arrondir_valeur
from grandeurs.reglages import Notation, StyleIncertitude, reglages
from grandeurs.simplification import simplificateur
from grandeurs.unites import Unite

__all__ = ["Grandeur"]

_CODES_PINT = frozenset("~PLHCDx")
_ANGLES_COLLES = frozenset({"°", "′", "″"})


def _tableau_incertain(valeur: object) -> bool:
    return (
        isinstance(valeur, np.ndarray)
        and valeur.dtype == object
        and valeur.size > 0
        and isinstance(valeur.flat[0], UFloat)
    )


def _centrale(x: Any) -> Any:
    """Valeur centrale d'un nombre ou d'une grandeur incertains ; inchangé sinon."""
    if isinstance(x, Grandeur):
        if isinstance(x.magnitude, UFloat) or _tableau_incertain(x.magnitude):
            return x._REGISTRY.Quantity(x.valeur, x._units)
        return x
    if isinstance(x, UFloat):
        return x.nominal_value
    if _tableau_incertain(x):
        return unumpy.nominal_values(x)
    return x


class Grandeur(pint.UnitRegistry.Quantity):  # type: ignore[misc]
    """Grandeur physique : valeur (éventuellement incertaine) et unité ; voir le module.

    On la crée par :func:`grandeurs.grandeur` ; toute opération entre grandeurs
    du registre rend une grandeur.
    """

    # Valeur et incertitude

    @property
    def valeur(self) -> Any:
        """Valeur centrale, dans l'unité de la grandeur (flottant ou tableau)."""
        m = self.magnitude
        if isinstance(m, UFloat):
            return m.nominal_value
        if _tableau_incertain(m):
            return unumpy.nominal_values(m)
        return m

    @property
    def incertitude(self) -> Any:
        """Incertitude-type, dans l'unité de la grandeur (0 pour une valeur exacte)."""
        m = self.magnitude
        if isinstance(m, UFloat):
            return m.std_dev
        if _tableau_incertain(m):
            return unumpy.std_devs(m)
        if isinstance(m, np.ndarray):
            return np.zeros(m.shape)
        return 0.0

    @property
    def incertitude_relative(self) -> Any:
        """Incertitude relative, |u/x| ; pour une unité affine, en unités SI."""
        grandeur = self if self._is_multiplicative else self.to_base_units()
        return np.abs(grandeur.incertitude / grandeur.valeur)

    @property
    def valeur_si(self) -> Any:
        """Valeur centrale en unités SI de base, pour revenir aux flottants."""
        return self.to_base_units().valeur

    @property
    def unite(self) -> Unite:
        """Unité, à égalité physique (voir :class:`grandeurs.Unite`)."""
        return Unite(self.units)

    @property
    def chiffres(self) -> int | None:
        """Chiffres significatifs que permet l'incertitude ; ``None`` si exacte."""
        if np.ndim(self.magnitude) or not self.incertitude:
            return None
        return self.arrondi().nombre_chiffres

    # Conversions

    def to(self, other: Any = None, *contexts: Any, **ctx_kwargs: Any) -> "Grandeur":
        """Conversion de pint, qui accepte aussi une :class:`grandeurs.Unite`."""
        if isinstance(other, Unite):
            other = other.pint_unit
        return super().to(other, *contexts, **ctx_kwargs)  # type: ignore[no-any-return]

    def vers(self, unite: Any) -> "Grandeur":
        """Convertit dans ``unite`` : ``v.vers("km.h-1")``, ``T.vers("°C")``."""
        return self.to(unite)

    def si(self) -> "Grandeur":
        """Convertit en SI, avec l'unité dérivée la plus simple (kg·m²·s⁻² → J)."""
        return simplificateur(self._REGISTRY).simplifier(self)  # type: ignore[no-any-return]

    # Écriture

    def arrondi(self, chiffres: int | None = None, *, elargie: bool = False) -> NombreArrondi:
        """Valeur arrondie d'après l'incertitude, ou à ``chiffres`` significatifs.

        L'arrondi porte sur l'incertitude-type (écriture courte, ``1.20(1)``), ou
        sur l'incertitude élargie si ``elargie`` (écriture « ± », ``1.20 ± 0.02``).
        Une valeur exacte est arrondie au réglage ``chiffres`` (3 par défaut).
        """
        if np.ndim(self.magnitude):
            raise TypeError("l'arrondi ne s'applique qu'à une grandeur scalaire")
        return arrondir_valeur(self.magnitude, chiffres, elargie=elargie)

    def texte(
        self,
        *,
        incertitude: bool | None = None,
        chiffres: int | None = None,
        decimale: str | None = None,
        notation: Notation | None = None,
        style: StyleIncertitude | None = None,
    ) -> str:
        """Écrit la grandeur : ``(1.20 ± 0.02) m·s⁻¹``, ``1.20 m·s⁻¹``, ``[1.00; 2.00] m``…

        Le style ``"pm"`` écrit l'incertitude élargie ``k·u`` (``k`` : réglage
        ``facteur_elargissement``, 2 par défaut), le style ``"courte"``
        l'incertitude-type ``u`` : ``1.20(1) m``.
        Les options valent par défaut les réglages (:func:`grandeurs.reglages`).
        ``chiffres`` impose un nombre de chiffres significatifs et masque alors
        l'incertitude. Un tableau est écrit élément par élément, avec la même
        règle d'arrondi, entre crochets et séparés par des points-virgules.
        """
        r = reglages()
        unite = self.unite.ecrire("texte")
        # Le SI colle °, ′ et ″ au nombre (30°), mais pas °C (20 °C).
        separateur = "" if unite in _ANGLES_COLLES else " "
        montrer = (r.afficher_incertitude if incertitude is None else incertitude) and not chiffres
        forme = (style or r.style_incertitude) if montrer else None

        def ecrire(m: Any) -> str:
            return arrondir_valeur(m, chiffres, elargie=forme == "pm").ecrire(
                notation=notation or r.notation, decimale=decimale or r.decimale, incertitude=forme
            )

        if np.ndim(self.magnitude):
            tableau = np.array2string(self.magnitude, separator="; ", formatter={"all": ecrire})
            return f"{tableau}{separateur}{unite}".rstrip()
        valeur = ecrire(self.magnitude)
        if forme == "pm" and self.incertitude and not valeur.startswith("(") and unite:
            valeur = f"({valeur})"
        return f"{valeur}{separateur}{unite}" if unite else valeur

    def latex(self, unite: Any = None, **options: Any) -> str:
        r"""Écrit ``\qty{1.20(1)}{m.s^{-1}}`` pour siunitx ; voir :func:`grandeurs.qty`."""
        # Import tardif : latex importe saisie, qui importe ce module.
        from grandeurs.latex import qty

        return qty(self, unite, **options)

    def __str__(self) -> str:
        return self.texte()

    def __format__(self, spec: str) -> str:
        if not spec:
            return self.texte()
        if _CODES_PINT & set(spec):
            return super().__format__(spec)  # type: ignore[no-any-return]
        return f"{format(self.magnitude, spec)} {self.unite.ecrire('texte')}".strip()

    def __repr__(self) -> str:
        return f'Grandeur({self._magnitude!r}, "{self._units}")'

    # Opérations qu'uncertainties déprécie sur ses nombres

    def compare(self, other: Any, op: Callable[[Any, Any], Any]) -> Any:
        """Comparaison d'ordre, sur les valeurs centrales.

        ``uncertainties`` déconseille de comparer des ``ufloat`` (``<`` y est
        déprécié) : on compare donc les valeurs centrales, ce que faisait
        ``uncertainties`` lui-même.
        """
        return super(Grandeur, _centrale(self)).compare(_centrale(other), op)

    def __abs__(self) -> Any:
        """Valeur absolue ; ``uncertainties`` déprécie ``abs`` sur un ``ufloat``.

        On change le signe des valeurs centrales négatives, ce qui garde
        l'incertitude et les corrélations (la dérivée de |x| vaut ±1).
        """
        m = self.magnitude
        if isinstance(m, UFloat):
            return -self if m.nominal_value < 0 else self
        if _tableau_incertain(m):
            negatives = unumpy.nominal_values(m) < 0
            return self._REGISTRY.Quantity(np.where(negatives, -m, m), self._units)
        return super().__abs__()

    def __round__(self, ndigits: int | None = None) -> Any:
        if isinstance(self.magnitude, UFloat) or _tableau_incertain(self.magnitude):
            raise TypeError(
                "une grandeur incertaine ne s'arrondit pas : son incertitude fixe ses "
                "chiffres ; pour l'écrire, utiliser .texte(chiffres=…) ou .arrondi()"
            )
        return super().__round__(ndigits)
