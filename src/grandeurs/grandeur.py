"""La grandeur physique : une quantité pint, plus incertitude, écriture et tolérance.

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
  (:meth:`texte`, ``str``), sortie siunitx (:meth:`latex`) ;
- la simplification en SI avec unités dérivées (:meth:`si`) et la conversion
  dans une unité écrite comme dans un manuel (:meth:`vers`) ;
- la tolérance envers les nombres nus. pint refuse ``longueur + 2`` ; ici le
  nombre est lu dans une unité (celle de l'autre opérande, ou l'unité SI, selon
  ``reglages().lecture_nombre``), avec un avertissement selon
  ``reglages().melange``. Un nombre nu est un nombre Python ou numpy, un
  ``ufloat``, ou une grandeur sans aucune unité (créée sans unité, ou rapport de
  deux grandeurs de même unité). Le zéro passe toujours sans avertissement,
  comme dans pint, pour que ``sum(grandeurs)`` fonctionne. L'égalité ``==``
  reste celle de pint : 1 m n'est pas le nombre 1.
"""

import reprlib
from collections.abc import Callable
from typing import Any

import numpy as np
import pint
from uncertainties import UFloat, unumpy

from grandeurs.chiffres import NombreArrondi, arrondir
from grandeurs.reglages import Notation, StyleIncertitude, reglages, signaler
from grandeurs.simplification import simplificateur
from grandeurs.unites import Unite

__all__ = ["Grandeur"]

_ADDITIVES = frozenset({"add", "subtract"})
_COMPARAISONS = frozenset({"less", "less_equal", "greater", "greater_equal"})
_CODES_PINT = frozenset("~PLHCDx")
_ANGLES_COLLES = frozenset({"°", "′", "″"})


def _tableau_incertain(valeur: object) -> bool:
    return (
        isinstance(valeur, np.ndarray)
        and valeur.dtype == object
        and valeur.size > 0
        and isinstance(valeur.flat[0], UFloat)
    )


def _nul(valeur: object) -> bool:
    """Zéro ou NaN (scalaire ou tableau), que pint accepte avec toute unité."""
    if isinstance(valeur, UFloat):
        return False
    tableau = np.asarray(valeur)
    if tableau.dtype.kind not in "biuf":
        return False
    return bool(np.all((tableau == 0) | np.isnan(tableau)))


def _pint(autre: Any) -> Any:
    return autre.pint_unit if isinstance(autre, Unite) else autre


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

    def arrondi(self, chiffres: int | None = None) -> NombreArrondi:
        """Valeur arrondie d'après l'incertitude (ou à ``chiffres`` significatifs)."""
        if np.ndim(self.magnitude):
            raise TypeError("l'arrondi ne s'applique qu'à une grandeur scalaire")
        incertitude = 0.0 if chiffres is not None else float(self.incertitude)
        return arrondir(
            float(self.valeur),
            incertitude,
            chiffres_incertitude=reglages().chiffres_incertitude,
            chiffres=chiffres,
        )

    def texte(
        self,
        *,
        incertitude: bool | None = None,
        chiffres: int | None = None,
        decimale: str | None = None,
        notation: Notation | None = None,
        style: StyleIncertitude | None = None,
    ) -> str:
        """Écrit la grandeur : ``(1.20 ± 0.01) m·s⁻¹``, ``1.20 m·s⁻¹``…

        Les options valent par défaut les réglages (:func:`grandeurs.reglages`).
        ``chiffres`` impose un nombre de chiffres significatifs et masque alors
        l'incertitude.
        """
        r = reglages()
        unite = self.unite.ecrire("texte")
        # Le SI colle °, ′ et ″ au nombre (30°), mais pas °C (20 °C).
        separateur = "" if unite in _ANGLES_COLLES else " "
        if np.ndim(self.magnitude):
            return f"{self.magnitude}{separateur}{unite}".rstrip()
        montrer = (r.afficher_incertitude if incertitude is None else incertitude) and not chiffres
        forme = (style or r.style_incertitude) if montrer else None
        nombre = self.arrondi(chiffres)
        valeur = nombre.ecrire(
            notation=notation or r.notation, decimale=decimale or r.decimale, incertitude=forme
        )
        if forme == "pm" and nombre.incertitude is not None and not valeur.startswith("("):
            valeur = f"({valeur})" if unite else valeur
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

    # Tolérance aux nombres nus

    def _sans_unite(self) -> bool:
        return bool(self.dimensionless and not self._units)

    def _nombre_nu(self, autre: object) -> bool:
        """``autre`` est-il un nombre sans unité non nul, face à une grandeur qui en a une ?"""
        if self.dimensionless:
            return False
        if isinstance(autre, pint.Quantity):
            return isinstance(autre, Grandeur) and autre._sans_unite() and not _nul(autre.magnitude)
        if isinstance(autre, (int, float, complex, np.number, np.ndarray, UFloat)):
            return not _nul(autre)
        return False

    def _lire(self, nombre: object, *, ecart: bool) -> "Grandeur":
        """Donne au nombre nu l'unité choisie par les réglages, et le signale.

        Dans une addition (``ecart``), un nombre ajouté à une unité affine est
        un écart : 20 °C + 5 donne 25 °C, et non une somme de deux températures.
        """
        r = reglages()
        magnitude = nombre.magnitude if isinstance(nombre, pint.Quantity) else nombre
        quantite: Any = self._REGISTRY.Quantity
        if r.lecture_nombre == "unite":
            lu = quantite(magnitude, self._units)
        else:
            lu = quantite(magnitude, self.to_base_units()._units)
        if ecart and not self._is_multiplicative:
            delta = self._REGISTRY.UnitsContainer(
                {f"delta_{nom}": p for nom, p in self._units.items()}
            )
            lu = quantite(magnitude, delta) if r.lecture_nombre == "unite" else lu.to(delta)
        apercu = reprlib.repr(magnitude)
        signaler(
            r.melange,
            f"nombre sans unité {apercu} lu en {Unite(lu.units)} "
            f"face à une grandeur en {self.unite} (lecture_nombre={r.lecture_nombre!r})",
        )
        return lu  # type: ignore[no-any-return]

    def _add_sub(self, other: Any, op: Callable[[Any, Any], Any]) -> Any:
        if self._nombre_nu(other):
            other = self._lire(other, ecart=True)
        elif isinstance(other, Grandeur) and other._nombre_nu(self):
            return other._lire(self, ecart=True)._add_sub(other, op)
        return super()._add_sub(other, op)

    def _iadd_sub(self, other: Any, op: Callable[[Any, Any], Any]) -> Any:
        if self._nombre_nu(other):
            other = self._lire(other, ecart=True)
        return super()._iadd_sub(other, op)

    def compare(self, other: Any, op: Callable[[Any, Any], Any]) -> Any:
        """Comparaison d'ordre, sur les valeurs centrales.

        ``uncertainties`` déconseille de comparer des ``ufloat`` (``<`` y est
        déprécié) : on compare donc les valeurs centrales, ce que faisait
        ``uncertainties`` lui-même.
        """
        if self._nombre_nu(other):
            other = self._lire(other, ecart=False)
        elif isinstance(other, Grandeur) and other._nombre_nu(self):
            return other._lire(self, ecart=False).compare(other, op)
        return super(Grandeur, _centrale(self)).compare(_centrale(other), op)

    def __array_ufunc__(self, ufunc: Any, method: str, *inputs: Any, **kwargs: Any) -> Any:
        nom = getattr(ufunc, "__name__", "")
        if method == "__call__" and len(inputs) == 2 and nom in _ADDITIVES | _COMPARAISONS:
            inputs = self._accorder(inputs, ecart=nom in _ADDITIVES)
            if nom in _COMPARAISONS:
                inputs = tuple(_centrale(x) for x in inputs)
        return super().__array_ufunc__(ufunc, method, *inputs, **kwargs)

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

    # Produit par une Unite : pint ne la connaît pas, on lui passe l'unité pint.

    def __mul__(self, other: Any) -> Any:
        return super().__mul__(_pint(other))

    def __rmul__(self, other: Any) -> Any:
        return super().__rmul__(_pint(other))

    def __truediv__(self, other: Any) -> Any:
        return super().__truediv__(_pint(other))

    def __rtruediv__(self, other: Any) -> Any:
        return super().__rtruediv__(_pint(other))

    @staticmethod
    def _accorder(operandes: tuple[Any, Any], *, ecart: bool) -> tuple[Any, Any]:
        """Lit dans l'unité de l'autre l'opérande nu d'une fonction numpy binaire."""
        a, b = operandes
        if isinstance(a, Grandeur) and a._nombre_nu(b):
            return a, a._lire(b, ecart=ecart)
        if isinstance(b, Grandeur) and b._nombre_nu(a):
            return b._lire(a, ecart=ecart), b
        return a, b
