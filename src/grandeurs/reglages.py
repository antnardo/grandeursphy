"""Réglages globaux : tolérance envers les valeurs sans unité, lecture et affichage.

L'API est volontairement permissive : une valeur dont on a oublié l'unité passe,
sans dimension, plutôt que de faire échouer un corrigé entier. Mais un oubli
d'unité est presque toujours une erreur, et doit pouvoir se voir. D'où un niveau
réglable pour chacune des deux situations où l'oubli se produit :

- ``sans_unite`` : une grandeur créée sans unité (``grandeur(3)``) ;
- ``melange`` : un nombre nu ajouté, soustrait ou comparé à une grandeur qui a
  une unité (``longueur + 2``).

Chaque niveau vaut ``"silence"`` (on accepte sans rien dire), ``"avertissement"``
(on accepte en émettant un :class:`SansUniteWarning`, filtrable par le module
standard :mod:`warnings`) ou ``"erreur"`` (on refuse : :class:`SansUniteError`).

Les réglages forment un objet figé ; on les change par :func:`configurer` ou, le
temps d'un bloc, par :func:`reglages_temporaires`. Un objet figé plutôt que des
variables de module modifiables : on ne peut pas changer un champ par erreur en
le croyant local, et le bloc ``with`` restaure exactement l'état d'avant.

Les réglages sont une variable globale du processus, non une ``ContextVar`` : un
fil d'exécution démarré après ``configurer(...)`` voit bien la configuration,
alors qu'une ``ContextVar`` lui rendrait les valeurs par défaut.
"""

import sys
import warnings
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal, TypeAlias, get_args

__all__ = [
    "Lecture",
    "Niveau",
    "Notation",
    "Reglages",
    "SansUniteError",
    "SansUniteWarning",
    "StyleIncertitude",
    "configurer",
    "reglages",
    "reglages_temporaires",
    "signaler",
]

Niveau: TypeAlias = Literal["silence", "avertissement", "erreur"]
Lecture: TypeAlias = Literal["unite", "si"]
Notation: TypeAlias = Literal["auto", "fixe", "scientifique", "ingenieur"]
StyleIncertitude: TypeAlias = Literal["pm", "courte"]


class SansUniteWarning(UserWarning):
    """Une valeur sans unité a été acceptée là où une unité était attendue."""


class SansUniteError(ValueError):
    """Une valeur sans unité a été refusée (niveau ``"erreur"``)."""


@dataclass(frozen=True, slots=True)
class Reglages:
    """Réglages du paquet ; voir le module pour leur raison d'être.

    Attributs :

    - ``sans_unite`` : niveau quand une grandeur est créée sans unité ;
    - ``melange`` : niveau quand un nombre nu rencontre une grandeur qui a une
      unité dans une addition, une soustraction ou une comparaison d'ordre ;
    - ``lecture_nombre`` : comment lire ce nombre nu. ``"unite"`` le lit dans
      l'unité de l'autre opérande (``12 cm + 3`` donne 15 cm) ; ``"si"`` le lit
      dans l'unité SI cohérente de la même dimension (``12 cm + 3`` donne 312 cm),
      ce qui convient quand les nombres nus viennent de calculs en flottants SI ;
    - ``chiffres_significatifs`` : une chaîne comme ``"1.20"`` porte une
      incertitude d'une unité sur son dernier chiffre ; sinon elle est exacte ;
    - ``chiffres_incertitude`` : nombre de chiffres significatifs gardés sur
      l'incertitude à l'affichage (la valeur est arrondie au même rang) ;
    - ``afficher_incertitude`` : afficher l'incertitude, ou seulement la valeur
      arrondie à ses chiffres significatifs ;
    - ``style_incertitude`` : à l'écran, ``"pm"`` donne ``(1.20 ± 0.01) m`` et
      ``"courte"`` donne ``1.20(1) m`` (la sortie LaTeX est toujours courte) ;
    - ``decimale`` : séparateur décimal, ``"."`` ou ``","`` ;
    - ``notation`` : ``"auto"``, ``"fixe"``, ``"scientifique"`` ou ``"ingenieur"``.
    """

    sans_unite: Niveau = "avertissement"
    melange: Niveau = "avertissement"
    lecture_nombre: Lecture = "unite"
    chiffres_significatifs: bool = True
    chiffres_incertitude: int = 1
    afficher_incertitude: bool = True
    style_incertitude: StyleIncertitude = "pm"
    decimale: str = "."
    notation: Notation = "auto"

    def __post_init__(self) -> None:
        self._verifier("sans_unite", self.sans_unite, get_args(Niveau))
        self._verifier("melange", self.melange, get_args(Niveau))
        self._verifier("lecture_nombre", self.lecture_nombre, get_args(Lecture))
        self._verifier("style_incertitude", self.style_incertitude, get_args(StyleIncertitude))
        self._verifier("notation", self.notation, get_args(Notation))
        self._verifier("decimale", self.decimale, (".", ","))
        if not isinstance(self.chiffres_incertitude, int) or self.chiffres_incertitude < 1:
            raise ValueError("chiffres_incertitude doit être un entier ≥ 1")

    @staticmethod
    def _verifier(nom: str, valeur: object, permis: tuple[object, ...]) -> None:
        if valeur not in permis:
            choix = ", ".join(repr(p) for p in permis)
            raise ValueError(f"réglage {nom} = {valeur!r} invalide ; choix : {choix}")


_actuels = Reglages()


def reglages() -> Reglages:
    """Réglages en vigueur."""
    return _actuels


def configurer(**changements: Any) -> Reglages:
    """Change les réglages pour tout le processus ; rend les réglages d'avant.

    >>> ancien = configurer(melange="erreur", decimale=",")
    """
    global _actuels
    ancien = _actuels
    _actuels = replace(_actuels, **changements)
    return ancien


@contextmanager
def reglages_temporaires(**changements: Any) -> Iterator[Reglages]:
    """Change les réglages le temps d'un bloc ``with``, puis restaure l'état d'avant."""
    global _actuels
    ancien = configurer(**changements)
    try:
        yield _actuels
    finally:
        _actuels = ancien


_DOSSIERS_INTERNES = (str(Path(__file__).resolve().parent),)


def _hors_paquet(nom_fichier: str) -> bool:
    """Le cadre appartient-il au code de l'utilisateur ?

    Les avertissements doivent désigner la ligne de l'utilisateur, pas celle de
    ce paquet ni de pint, qui s'intercale entre l'opérateur et notre code ; la
    profondeur varie selon l'opération, d'où ce parcours de la pile (le
    paramètre ``skip_file_prefixes`` de :func:`warnings.warn` n'existe qu'à
    partir de Python 3.12).
    """
    chemin = str(Path(nom_fichier).resolve()) if nom_fichier[:1] not in "<" else nom_fichier
    if chemin.startswith(_DOSSIERS_INTERNES):
        return False
    morceaux = Path(chemin).parts
    return "pint" not in morceaux and "uncertainties" not in morceaux


def _profondeur_utilisateur() -> int:
    cadre = sys._getframe(1)
    profondeur = 1
    while cadre is not None and not _hors_paquet(cadre.f_code.co_filename):
        cadre = cadre.f_back  # type: ignore[assignment]
        profondeur += 1
    return profondeur


def signaler(niveau: Niveau, message: str) -> None:
    """Applique un niveau à un oubli d'unité : rien, un avertissement ou une erreur."""
    if niveau == "silence":
        return
    if niveau == "erreur":
        raise SansUniteError(message)
    warnings.warn(message, SansUniteWarning, stacklevel=_profondeur_utilisateur())
