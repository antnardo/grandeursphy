"""Unités du système CGS, en grandeurs SI (brochure du BIPM, 8e édition, tableau 9)."""

import math

from grandeurs.constantes._fiches import CGS, exacte

__all__ = [
    "DYN",
    "ERG",
    "GAL_CGS",
    "GAUSS",
    "MX",
    "OE",
    "PHOT",
    "POISE",
    "STATC",
    "STILB",
    "STOKES",
]

ERG = exacte("ERG", 1e-7, "J", "erg", CGS)
DYN = exacte("DYN", 1e-5, "N", "dyne", CGS)
POISE = exacte("POISE", 0.1, "Pa*s", "poise", CGS)
STOKES = exacte("STOKES", 1e-4, "m^2/s", "stokes", CGS)
STILB = exacte("STILB", 1e4, "cd/m^2", "stilb", CGS)
PHOT = exacte("PHOT", 1e4, "lx", "phot", CGS)
GAL_CGS = exacte("GAL_CGS", 1e-2, "m/s^2", "gal, unité CGS d'accélération", CGS)
MX = exacte("MX", 1e-8, "Wb", "maxwell", CGS)
GAUSS = exacte("GAUSS", 1e-4, "T", "gauss", CGS)
OE = exacte("OE", 1000 / (4 * math.pi), "A/m", "œrsted", CGS)
STATC = exacte(
    "STATC",
    1 / 2997924580,
    "C",
    "statcoulomb (franklin), unité de charge du système CGS électrostatique",
    "définition CGS-ues : 1 C = 10 c (en cm/s) statC",
)
