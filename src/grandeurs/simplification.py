"""Simplification d'une unité en SI, avec les unités dérivées nommées (N, J, W, V, Ω…).

pint propose ``to_base_units`` (tout en kg, m, s, A…), ``to_reduced_units``
(simplifie sans changer d'unités) et ``to_preferred``, qui cherche une
combinaison d'unités préférées ; essayé avec N, J, W, Pa, C, V, Ω, F, H, T, Wb
et Hz, ce dernier écrit une accélération « Hz·W/N » et une éclairement
« C·Hz²·T ». D'où cet algorithme plus étroit, mais prévisible :

1. on passe en unités de base SI (kg, m, s, A, mol, K, cd ; un radian
   éventuel est gardé tel quel) ;
2. si la dimension ne contient ni masse ni courant, on s'arrête : m·s⁻², m²·s⁻¹,
   mol·m⁻³ restent ainsi, et un N/kg ne remplace jamais un m·s⁻² ;
3. sinon on essaie chaque unité dérivée, à la puissance 1 ou −1, complétée par
   des unités de base, et l'on garde l'écriture la plus courte : la somme des
   valeurs absolues des exposants, puis le nombre de symboles. En cas
   d'égalité, les unités de base l'emportent, puis l'ordre de la liste
   (électriques d'abord : un champ électrique s'écrit V·m⁻¹ et non N·C⁻¹).

Le hertz n'est jamais choisi : une dimension « temps⁻¹ » est aussi bien une
fréquence (Hz), une activité (Bq) qu'une vitesse angulaire (rad/s, le radian
étant sans dimension), et seul l'utilisateur sait laquelle ; on écrit s⁻¹. De
même J/kg reste m²·s⁻², et N·m devient J. On convertit explicitement par
``.vers("Hz")`` ou ``.vers("J.kg-1")``.
"""

from functools import lru_cache
from typing import Any

__all__ = ["BASES_SI", "DERIVEES_SI", "SimplificateurSI", "simplificateur"]

BASES_SI = ("kilogram", "meter", "second", "ampere", "mole", "kelvin", "candela")
DERIVEES_SI = (
    "volt",
    "ohm",
    "siemens",
    "farad",
    "henry",
    "tesla",
    "weber",
    "coulomb",
    "joule",
    "watt",
    "newton",
    "pascal",
)

_MASSE_OU_COURANT = (BASES_SI.index("kilogram"), BASES_SI.index("ampere"))

Vecteur = tuple[float, ...]


class SimplificateurSI:
    """Choisit l'écriture SI la plus courte d'une unité ; voir le module."""

    def __init__(self, registre: Any, derivees: tuple[str, ...] = DERIVEES_SI) -> None:
        self._registre = registre
        self._derivees = [(nom, self._vecteur(nom)[0]) for nom in derivees]

    def unites(self, unites: Any) -> Any:
        """Unités SI simplifiées (``UnitsContainer``) équivalentes à ``unites``."""
        vecteur, autres = self._vecteur(unites)
        choix: dict[str, float] = {}
        meilleur = (*self._cout(vecteur, 0), -1)
        if any(vecteur[i] for i in _MASSE_OU_COURANT):
            for rang, (nom, derivee) in enumerate(self._derivees):
                for puissance in (1, -1):
                    reste = tuple(v - puissance * d for v, d in zip(vecteur, derivee, strict=True))
                    cout = (*self._cout(reste, 1), rang)
                    if cout < meilleur:
                        meilleur, choix = cout, {nom: puissance, **self._termes(reste)}
        if not choix:
            choix = self._termes(vecteur)
        choix.update(autres)
        return self._registre.UnitsContainer(choix)

    def simplifier(self, quantite: Any) -> Any:
        """Quantité convertie dans ses unités SI simplifiées."""
        return quantite.to(self.unites(quantite._units))

    def _vecteur(self, unites: Any) -> tuple[Vecteur, dict[str, float]]:
        """Exposants sur les unités de base SI, et unités de base hors SI (radian…)."""
        base = self._registre.Quantity(1, unites).to_base_units()._units
        vecteur = tuple(float(base.get(nom, 0)) for nom in BASES_SI)
        autres = {nom: p for nom, p in base.items() if nom not in BASES_SI}
        return vecteur, autres

    @staticmethod
    def _cout(vecteur: Vecteur, derivees: int) -> tuple[float, int]:
        return (
            sum(abs(v) for v in vecteur) + derivees,
            sum(1 for v in vecteur if v) + derivees,
        )

    @staticmethod
    def _termes(vecteur: Vecteur) -> dict[str, float]:
        return {nom: _entier(v) for nom, v in zip(BASES_SI, vecteur, strict=True) if v}


def _entier(valeur: float) -> float:
    return int(valeur) if float(valeur).is_integer() else valeur


@lru_cache(maxsize=8)
def simplificateur(registre: Any) -> SimplificateurSI:
    """Simplificateur attaché à un registre (un seul par registre)."""
    return SimplificateurSI(registre)
