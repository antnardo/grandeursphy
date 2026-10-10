"""Réglages globaux : grandeur créée sans unité, lecture et affichage.

Une grandeur créée sans unité (``grandeur(3)``) est presque toujours un oubli.
Elle passe, sans dimension, plutôt que de faire échouer un corrigé entier, mais
l'oubli est signalé selon ``sans_unite`` : ``"silence"`` (on accepte sans rien
dire), ``"avertissement"`` (on accepte en émettant un :class:`SansUniteWarning`,
filtrable par le module standard :mod:`warnings`) ou ``"erreur"`` (on refuse :
:class:`SansUniteError`). Pour une grandeur réellement sans dimension, on
l'écrit : ``grandeur(0.5, "")``.

Les réglages forment un objet figé ; on les change par :func:`configurer` ou, le
temps d'un bloc, par :func:`reglages_temporaires`. Un objet figé plutôt que des
variables de module modifiables : on ne peut pas changer un champ par erreur en
le croyant local, et le bloc ``with`` restaure exactement l'état d'avant.

Les réglages sont une variable globale du processus, non une ``ContextVar`` : un
fil d'exécution démarré après ``configurer(...)`` voit bien la configuration,
alors qu'une ``ContextVar`` lui rendrait les valeurs par défaut.
"""

import warnings
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import Any, Literal, TypeAlias, get_args

__all__ = [
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
Notation: TypeAlias = Literal["auto", "fixe", "scientifique", "ingenieur"]
StyleIncertitude: TypeAlias = Literal["pm", "courte"]


class SansUniteWarning(UserWarning):
    """Une grandeur a été créée sans unité."""


class SansUniteError(ValueError):
    """Une grandeur sans unité a été refusée (niveau ``"erreur"``)."""


@dataclass(frozen=True, slots=True)
class Reglages:
    """Réglages du paquet ; voir le module pour leur raison d'être.

    Attributs :

    - ``sans_unite`` : niveau quand une grandeur est créée sans unité ;
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
    chiffres_significatifs: bool = True
    chiffres_incertitude: int = 1
    afficher_incertitude: bool = True
    style_incertitude: StyleIncertitude = "pm"
    decimale: str = "."
    notation: Notation = "auto"

    def __post_init__(self) -> None:
        self._verifier("sans_unite", self.sans_unite, get_args(Niveau))
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

    >>> ancien = configurer(decimale=",")
    >>> reglages().decimale
    ','
    >>> configurer(decimale=ancien.decimale).decimale
    ','
    """
    global _actuels
    ancien = _actuels
    _actuels = replace(_actuels, **changements)
    return ancien


@contextmanager
def reglages_temporaires(**changements: Any) -> Iterator[Reglages]:
    """Change les réglages le temps d'un bloc ``with``, puis restaure l'état d'avant.

    >>> with reglages_temporaires(decimale=","):
    ...     reglages().decimale
    ','
    >>> reglages().decimale
    '.'
    """
    global _actuels
    ancien = configurer(**changements)
    try:
        yield _actuels
    finally:
        _actuels = ancien


def signaler(niveau: Niveau, message: str) -> None:
    """Applique un niveau à un oubli d'unité : rien, un avertissement ou une erreur.

    L'avertissement désigne la ligne qui a appelé la fonction publique d'où vient
    le signalement (``grandeur(3)``), deux cadres au-dessus de celle-ci.
    """
    if niveau == "silence":
        return
    if niveau == "erreur":
        raise SansUniteError(message)
    warnings.warn(message, SansUniteWarning, stacklevel=3)
