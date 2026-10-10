"""Les constantes de :mod:`grandeurs.constantes` en simples flottants SI.

Les corrigés existants calculent en flottants (``R_GP * T``) et formatent le
résultat (``f"{x:.3e}"``) ; une grandeur y changerait le type du résultat et
son écriture. Ce module leur donne les mêmes noms qu'avant, en ``float``,
valeur centrale exprimée en unités SI de base (kg, m, s, A, K, mol, cd ; le
radian pour les angles) : ``from grandeurs.flottants import R_GP``.

Les valeurs viennent des grandeurs de :mod:`grandeurs.constantes`, module par
module (:mod:`grandeurs.flottants.astro`, :mod:`grandeurs.flottants.cgs`,
:mod:`grandeurs.flottants.us` miroitent les sous-modules du même nom), si bien
que les deux ne peuvent pas diverger. Les constantes exactes (c, h, e, k, N_A
et ce qui s'en déduit : ħ, R…) ont les mêmes flottants qu'avec CODATA 2018 ;
les constantes mesurées (ε₀, mₑ, G…) ont leur valeur CODATA 2022.
"""

from grandeurs import constantes as _constantes
from grandeurs.flottants._miroir import exporter as _exporter

__all__ = _exporter(_constantes, globals())

from grandeurs.flottants import astro, cgs, us  # noqa: F401
