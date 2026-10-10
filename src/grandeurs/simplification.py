"""Simplification d'une unité en SI, avec les unités dérivées nommées (N, J, W, V, Ω…).

pint propose ``to_base_units`` (tout en kg, m, s, A…), ``to_reduced_units``
(simplifie sans changer d'unités) et ``to_preferred``, qui cherche une
combinaison d'unités préférées ; essayé avec N, J, W, Pa, C, V, Ω, F, H, T, Wb
et Hz, il écrit une accélération « Hz·W/N » et un éclairement (kg·s⁻³)
« C·Hz²·T ». D'où cet algorithme plus étroit, mais prévisible :

1. on passe en unités de base SI (kg, m, s, A, mol, K, cd ; un radian ou un
   ``count`` éventuel est gardé tel quel) ;
2. si cette écriture de base est celle d'une unité de la table
   :data:`PREFEREES_SI` (N/m, S/m, C/kg, lm, lx, Bq, V/m, Pa·s, J/(mol·K)…),
   c'est elle qu'on écrit : la table dit ce qu'un physicien attend là où le
   coût minimal choisirait T·A pour une raideur ou Ω⁻¹·m⁻¹ pour une
   conductivité ;
3. sinon, si la dimension ne contient ni masse ni courant, on s'arrête : m·s⁻²,
   m²·s⁻¹, mol·m⁻³ restent ainsi, et un N/kg ne remplace jamais un m·s⁻² ;
4. sinon on essaie chaque unité dérivée, à la puissance 1 ou −1, complétée par
   des unités de base, et l'on garde l'écriture la plus courte : la somme des
   valeurs absolues des exposants, puis le nombre de symboles. En cas
   d'égalité, les unités de base l'emportent, puis l'ordre de la liste
   (électriques d'abord).

Le hertz n'est jamais choisi : une dimension « temps⁻¹ » est aussi bien une
fréquence (Hz) qu'une vitesse angulaire (rad/s, le radian étant sans
dimension), et seul l'utilisateur sait laquelle ; on écrit s⁻¹. Le gray et le
sievert (J/kg) ont l'écriture de base d'une énergie massique ou d'un carré de
vitesse, m²·s⁻² : ils ne sont pas choisis non plus. On convertit explicitement
par ``.vers("Hz")``, ``.vers("Gy")``. Le becquerel, lui, est reconnu : pint
l'écrit ``count/s``, ce qui le distingue d'une fréquence.
"""

from functools import lru_cache
from typing import Any

__all__ = ["BASES_SI", "DERIVEES_SI", "PREFEREES_SI", "SimplificateurSI", "simplificateur"]

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
# Unités consultées avant le coût minimal, par leur écriture en unités de base.
# Deux entrées de même écriture de base (V/m et N/C) seraient une erreur.
PREFEREES_SI = (
    "N",
    "Pa",
    "J",
    "W",
    "C",
    "V",
    "F",
    "Ω",
    "S",
    "Wb",
    "T",
    "H",
    "lm",
    "lx",
    "Bq",
    "N/m",
    "C/kg",
    "S/m",
    "Ω.m",
    "V/m",
    "A/m",
    "H/m",
    "F/m",
    "Pa.s",
    "W/(m.K)",
    "J/(kg.K)",
    "J/(mol.K)",
    "J/K",
    "J/mol",
    "W/m2",
)

_MASSE_OU_COURANT = (BASES_SI.index("kilogram"), BASES_SI.index("ampere"))

Vecteur = tuple[float, ...]


class SimplificateurSI:
    """Choisit l'écriture SI d'une unité : table des préférées, puis coût minimal."""

    def __init__(
        self,
        registre: Any,
        derivees: tuple[str, ...] = DERIVEES_SI,
        preferees: tuple[str, ...] = PREFEREES_SI,
    ) -> None:
        self._registre = registre
        self._derivees = [(nom, self._vecteur(nom)[0]) for nom in derivees]
        self._preferees: dict[Any, Any] = {}
        for texte in preferees:
            cle = self._base(texte)
            if cle in self._preferees:
                raise ValueError(f"unités préférées de même écriture de base : {texte}")
            self._preferees[cle] = registre.parse_units(texte)._units

    def unites(self, unites: Any) -> Any:
        """Unités SI simplifiées (``UnitsContainer``) équivalentes à ``unites``."""
        base = self._base(unites)
        if base in self._preferees:
            return self._preferees[base]
        vecteur, autres = self._decomposer(base)
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

    def _base(self, unites: Any) -> Any:
        """Écriture en unités de base (``UnitsContainer``), radian et count compris."""
        return self._registre.Quantity(1, unites).to_base_units()._units

    def _vecteur(self, unites: Any) -> tuple[Vecteur, dict[str, float]]:
        return self._decomposer(self._base(unites))

    @staticmethod
    def _decomposer(base: Any) -> tuple[Vecteur, dict[str, float]]:
        """Exposants sur les unités de base SI, et unités de base hors SI (radian…)."""
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
