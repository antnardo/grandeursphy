"""Écriture des unités : à l'écran (m·s⁻¹), en ASCII (m.s-1) et pour siunitx (m.s^{-1}).

pint sait écrire ses unités, mais pas dans les usages français : il écrit le
litre « l », le degré « deg », range les unités par ordre alphabétique et met
les exposants négatifs sous une barre de fraction. On écrit ici les unités
comme dans les manuels : exposants négatifs plutôt que barre (J·mol⁻¹·K⁻¹),
exposants positifs d'abord, dans l'ordre où l'unité a été construite.

La sortie siunitx est « littérale », comme dans les documents existants
(``\\SI{2,09e3}{kg.m^{-3}}``) : lettres des symboles, point pour le produit,
exposants entre accolades ; seuls les symboles qui ne sont pas des lettres
latines passent par une macro (``\\micro m``, ``k\\ohm``, ``\\degreeCelsius``).
"""

from collections.abc import Iterable
from functools import lru_cache
from typing import Any, Literal, TypeAlias

__all__ = ["MACROS_SIUNITX", "FormateurUnites", "Style", "formateur"]

Style: TypeAlias = Literal["texte", "ascii", "siunitx"]

# Symboles de base remplacés : usage français (L, °, tr) ou symbole plus lisible.
_SYMBOLES = {
    "liter": "L",
    "degree": "°",
    "arcminute": "′",
    "arcsecond": "″",
    "turn": "tr",
    "planck_constant": "h",
}

# Symboles qui passent par une macro siunitx ; lu à l'envers par ``grandeurs.latex.lire_qty``.
MACROS_SIUNITX = {
    "°C": r"\degreeCelsius",
    "Δ°C": r"\degreeCelsius",
    "°": r"\degree",
    "′": r"\arcminute",
    "″": r"\arcsecond",
    "Ω": r"\ohm",
    "Å": r"\angstrom",
    "%": r"\percent",
}

_EXPOSANTS = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


class FormateurUnites:
    """Écrit un conteneur d'unités pint (nom → exposant) dans un des trois styles."""

    def __init__(self, registre: Any) -> None:
        self._registre = registre

    def ecrire(self, unites: Any, style: Style = "texte") -> str:
        """Écrit ``unites`` (``UnitsContainer``, ``Unit`` ou quantité pint)."""
        conteneur = getattr(unites, "_units", unites)
        termes = list(conteneur.items())
        ordonnes = [t for t in termes if t[1] > 0] + [t for t in termes if t[1] < 0]
        separateur = "·" if style == "texte" else "."
        return separateur.join(self._terme(nom, puissance, style) for nom, puissance in ordonnes)

    def symboles(self, unites: Any) -> Iterable[tuple[str, str, float]]:
        """Préfixe, symbole et exposant de chaque unité, pour d'autres écritures."""
        conteneur = getattr(unites, "_units", unites)
        for nom, puissance in conteneur.items():
            prefixe, base = self._symbole(nom)
            yield prefixe, base, puissance

    def _terme(self, nom: str, puissance: float, style: Style) -> str:
        prefixe, base = self._symbole(nom)
        if style == "siunitx":
            symbole = self._siunitx(prefixe, base)
            return symbole if puissance == 1 else f"{symbole}^{{{_nombre(puissance)}}}"
        symbole = prefixe + base
        if puissance == 1:
            return symbole
        exposant = _nombre(puissance)
        if style == "ascii":
            return (
                f"{symbole}{exposant}" if float(puissance).is_integer() else f"{symbole}^{exposant}"
            )
        if float(puissance).is_integer():
            return symbole + exposant.translate(_EXPOSANTS)
        return f"{symbole}^{exposant}"

    @lru_cache(maxsize=512)  # noqa: B019 - un seul formateur par registre, vivant tout le programme
    def _symbole(self, nom: str) -> tuple[str, str]:
        """Sépare le préfixe du symbole de base (``kΩ`` → ``k``, ``Ω``)."""
        complet = self._registre.get_symbol(nom).replace("μ", "µ")
        candidats = self._registre.parse_unit_name(nom)
        if not candidats:
            return "", complet
        _, base, _ = candidats[0]
        symbole_base = self._registre.get_symbol(base).replace("μ", "µ")
        prefixe = complet[: -len(symbole_base)] if complet.endswith(symbole_base) else ""
        if not complet.endswith(symbole_base):
            symbole_base = complet
        return prefixe, _SYMBOLES.get(base, symbole_base)

    @staticmethod
    def _siunitx(prefixe: str, base: str) -> str:
        macro = MACROS_SIUNITX.get(base, base)
        if prefixe == "µ":
            return r"\micro" + (macro if macro.startswith("\\") else " " + macro)
        return prefixe + macro


def _nombre(puissance: float) -> str:
    """Exposant sans « .0 » inutile : 2 et non 2.0, 0.5 reste 0.5."""
    return str(int(puissance)) if float(puissance).is_integer() else repr(float(puissance))


@lru_cache(maxsize=8)
def formateur(registre: Any) -> FormateurUnites:
    """Formateur attaché à un registre (un seul par registre)."""
    return FormateurUnites(registre)
