"""Constantes astronomiques : UAI, Soleil, Terre, Lune, en grandeurs.

Les valeurs nominales de l'UAI (résolution B3 de 2015) sont exactes par
convention ; les masses s'en déduisent par G, avec son incertitude. Le reste
(Terre WGS 84, orbites, Lune) est daté dans sa fiche (:func:`decrire`).
"""

import math

from grandeurs.constantes import C, G
from grandeurs.constantes._fiches import CODATA, UAI_2015_B3, deduite, exacte, mesuree

__all__ = [
    "AL",
    "D_TL",
    "D_TS",
    "H_0",
    "PC",
    "UA",
    "YEAR_JULIAN",
    "YEAR_SIDERAL",
    "YEAR_TROPIC",
    "GM_earth",
    "GM_sun",
    "L_sun",
    "M_earth",
    "M_moon",
    "M_sun",
    "R_earth",
    "R_moon",
    "R_sun",
    "S_sun",
    "T_sun",
    "e_earth",
    "e_moon",
    "f_earth",
]

_LUNE_NASA = "NASA NSSDC, « Moon Fact Sheet »"
_STANDISH = (
    "E. M. Standish, JPL SSD, « Approximate Positions of the Planets », table 1 "
    "(1800-2050), barycentre Terre-Lune"
)
_WGS84 = "WGS 84, NGA.STND.0036 (2014) : paramètre de définition"

UA = exacte("UA", 149597870700, "m", "unité astronomique", "UAI 2012, résolution B2 (exacte)")
PC = exacte(
    "PC",
    648000 / math.pi * 149597870700,
    "m",
    "parsec, 648 000/π ua",
    "UAI 2015, résolution B2 (exacte)",
)
YEAR_JULIAN = exacte(
    "YEAR_JULIAN", 365.25 * 86400, "s", "année julienne, 365,25 j", "UAI (définition)"
)
AL = deduite(
    "AL",
    (C * YEAR_JULIAN).to("m"),
    "année-lumière, c × année julienne",
    "UAI (définition)",
)
YEAR_SIDERAL = exacte(
    "YEAR_SIDERAL",
    365.256363004 * 86400,
    "s",
    "année sidérale, 365,256 363 004 j (J2000)",
    "Astronomical Almanac, glossaire",
)
YEAR_TROPIC = exacte(
    "YEAR_TROPIC",
    365.24219 * 86400,
    "s",
    "année tropique moyenne, 365,242 19 j (J2000)",
    "J. Laskar, A&A 157, 59 (1986), arrondi",
)
H_0 = mesuree(
    "H_0",
    67.4,
    0.5,
    "km/s/Mpc",
    "constante de Hubble (les mesures locales donnent 73 km/s/Mpc : « tension de Hubble »)",
    "Planck Collaboration, A&A 641, A6 (2020)",
)

# Soleil

GM_sun = exacte(
    "GM_sun", 1.3271244e20, "m^3/s^2", "paramètre gravitationnel du Soleil", UAI_2015_B3
)
M_sun = deduite(
    "M_sun", (GM_sun / G).to("kg"), "masse du Soleil, (GM)☉/G", f"{UAI_2015_B3} ; G {CODATA}"
)
R_sun = exacte("R_sun", 6.957e8, "m", "rayon du Soleil", UAI_2015_B3)
L_sun = exacte("L_sun", 3.828e26, "W", "luminosité du Soleil", UAI_2015_B3)
S_sun = exacte("S_sun", 1361, "W/m^2", "éclairement solaire total à 1 ua", UAI_2015_B3)
T_sun = exacte("T_sun", 5772, "K", "température effective du Soleil", UAI_2015_B3)

# Terre

GM_earth = exacte(
    "GM_earth", 3.986004e14, "m^3/s^2", "paramètre gravitationnel de la Terre", UAI_2015_B3
)
M_earth = deduite(
    "M_earth",
    (GM_earth / G).to("kg"),
    "masse de la Terre, (GM)⊕/G",
    f"{UAI_2015_B3} ; G {CODATA}",
)
R_earth = exacte(
    "R_earth",
    6378137,
    "m",
    "rayon équatorial de la Terre (demi-grand axe de l'ellipsoïde)",
    _WGS84,
)
f_earth = exacte(
    "f_earth", 1 / 298.257223563, "", "aplatissement de l'ellipsoïde terrestre", _WGS84
)
e_earth = exacte("e_earth", 0.01671123, "", "excentricité de l'orbite terrestre", _STANDISH)
D_TS = exacte(
    "D_TS",
    1.00000261 * 149597870700,
    "m",
    "demi-grand axe de l'orbite terrestre, 1,000 002 61 ua",
    _STANDISH,
)

# Lune

M_moon = deduite(
    "M_moon",
    M_earth * 0.0123000371,
    "masse de la Lune, M⊕ × 0,012 300 0371",
    "rapport des masses UAI 2009 (Luzum et al., Celest. Mech. Dyn. Astron. 110, 293, 2011)",
)
R_moon = exacte(
    "R_moon",
    1.7374e6,
    "m",
    "rayon moyen de la Lune",
    "UAI, groupe WGCCRE (Archinal et al., Celest. Mech. Dyn. Astron. 130, 22, 2018)",
)
D_TL = exacte(
    "D_TL", 3.84399e8, "m", "demi-grand axe de l'orbite lunaire", f"{_LUNE_NASA} (0,3844 Gm)"
)
e_moon = exacte("e_moon", 0.0549, "", "excentricité de l'orbite lunaire", _LUNE_NASA)
