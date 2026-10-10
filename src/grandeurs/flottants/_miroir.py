"""Le miroir en flottants d'un module de constantes."""

from types import ModuleType
from typing import Any

from grandeurs.constantes._fiches import FICHES


def exporter(module: ModuleType, espace: dict[str, Any]) -> list[str]:
    """Pose dans ``espace`` chaque constante publique de ``module``, en flottant SI.

    Rend la liste des noms, à donner à ``__all__`` : les deux modules ne peuvent
    pas diverger.
    """
    noms = [nom for nom in module.__all__ if nom in FICHES]
    for nom in noms:
        espace[nom] = float(getattr(module, nom).valeur_si)
    return noms
