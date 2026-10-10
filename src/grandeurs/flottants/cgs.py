"""Miroir en flottants SI de :mod:`grandeurs.constantes.cgs`."""

from grandeurs.constantes import cgs as _constantes
from grandeurs.flottants._miroir import exporter as _exporter

__all__ = _exporter(_constantes, globals())
