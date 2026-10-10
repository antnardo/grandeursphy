"""Miroir en flottants SI de :mod:`grandeurs.constantes.astro`."""

from grandeurs.constantes import astro as _constantes
from grandeurs.flottants._miroir import exporter as _exporter

__all__ = _exporter(_constantes, globals())
