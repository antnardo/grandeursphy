"""Le registre d'unités unique du paquet, configuré une fois pour toutes.

pint exige que les quantités qu'on combine viennent du même registre ; il en
faut donc un seul, créé ici et déclaré registre d'application de pint
(:func:`pint.set_application_registry`), pour que le dépicklage et les autres
bibliothèques qui utilisent pint retrouvent les mêmes unités.

Configuration :

- la classe des quantités est :class:`grandeurs.Grandeur` ;
- la notation de manuel (``m.s-1``) est traduite avant toute analyse de pint
  (:mod:`grandeurs.notation`, branché comme préprocesseur) ;
- ``autoconvert_offset_to_baseunit`` : une température en °C qui entre dans un
  produit est convertie en kelvins, si bien que ``R * T`` avec T = 20 °C donne
  le bon résultat au lieu d'une erreur ;
- système SI, et écriture abrégée par défaut (``~P``) pour ce que pint écrit
  lui-même ;
- quelques noms français que pint ignore : ``j`` (jour), ``an`` (année),
  ``tr`` (tour, d'où ``tr/min``), ``Torr``. On n'ajoute pas ``ua`` ni ``al`` :
  pint les lit déjà comme micro-année et attolitre ; on écrit ``au`` et ``ly``.
"""

import pint

from grandeurs.grandeur import Grandeur
from grandeurs.notation import traduire_notation

__all__ = ["Registre", "creer_registre", "ureg"]

_DEFINITIONS = (
    "@alias day = j",
    "@alias year = an",
    "@alias turn = tr",
    "@alias torr = Torr",
)


class Registre(pint.UnitRegistry):
    """Registre pint dont les quantités sont des :class:`grandeurs.Grandeur`."""

    Quantity = Grandeur  # type: ignore[assignment]


def creer_registre() -> Registre:
    """Crée un registre configuré ; le paquet n'en utilise qu'un, :data:`ureg`."""
    registre = Registre(
        autoconvert_offset_to_baseunit=True,
        preprocessors=[traduire_notation],
        system="SI",
    )
    registre.formatter.default_format = "~P"
    for definition in _DEFINITIONS:
        registre.define(definition)
    return registre


ureg = creer_registre()
pint.set_application_registry(ureg)
