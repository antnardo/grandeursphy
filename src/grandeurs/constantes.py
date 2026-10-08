"""Constantes physiques, unités hors SI et données astronomiques, en grandeurs.

Chaque constante est une :class:`grandeurs.Grandeur` : valeur, incertitude-type
(un ``ufloat`` quand elle n'est pas nulle) et unité. La même liste existe en
simples flottants SI dans :mod:`grandeurs.flottants`, pour les calculs qui
n'utilisent pas d'unités.

Sources :

- constantes fondamentales : CODATA, lu dans :mod:`scipy.constants` ; il faut
  scipy ≥ 1.15, première version à fournir CODATA 2022 (scipy 1.14 et avant
  donnent CODATA 2018). Les constantes exactes depuis 2019 (c, h, e, k, N_A…)
  ont une incertitude nulle ; les constantes qui s'en déduisent exactement
  (ħ, R, F, K_J…) aussi ;
- ce que scipy n'a pas : constantes astronomiques nominales de l'UAI, Terre,
  Lune, unités CGS, masse du W ; la source de chaque valeur est dans
  :data:`FICHES` et dans :func:`decrire`.

Les incertitudes des constantes CODATA sont traitées comme indépendantes :
CODATA publie leurs corrélations, mais scipy ne les fournit pas. Un rapport de
deux constantes mesurées (``M_P / M_E``) a donc une incertitude surestimée ;
:func:`codata` donne directement la valeur ajustée (``codata("proton-electron
mass ratio")``).

Noms : ceux de l'ancien paquet ``constantes``, sans les masquages qui faisaient
qu'un même nom désignait deux grandeurs. Les trois noms en conflit gardent le
sens qu'``import constantes`` leur donnait effectivement, et l'autre sens reçoit
un nom propre :

- ``G_0`` : pesanteur normale ; le quantum de conductance devient
  ``G_CONDUCTANCE`` ;
- ``HA`` : énergie de Hartree ; l'hectare devient ``HECTARE`` ;
- ``GAL`` : gal (unité CGS d'accélération) ; le gallon américain devient
  ``GAL_US``.

Valeurs corrigées par rapport à l'ancien paquet : pouce (0,0254 m et non
0,254 m, et avec lui pied, yard, mile), gallon (en m³), zéro Celsius
(273,15 K et non 273,16 K), rayon lunaire (1 737,4 km et non 1,737 km),
température de Planck (avec la masse de Planck), magnéton nucléaire (avec la
masse du proton), G (CODATA 2022 au lieu de 2014), K_cd (683 lm/W ; les 540 THz
sont ``NU_CD``), œrsted (en A/m), constantes astronomiques (UAI 2015).
"""

import math
from dataclasses import dataclass
from typing import Any

import scipy
from scipy.constants import physical_constants
from uncertainties import ufloat

from grandeurs.grandeur import Grandeur
from grandeurs.registre import ureg

__all__ = [
    "AL",
    "ALPHA",
    "ANGSTROM",
    "ATM",
    "A_0",
    "BAR",
    "BARN",
    "CD",
    "DA",
    "DAY",
    "DEG",
    "DELTA_NU_CS",
    "DYN",
    "D_0",
    "D_TL",
    "D_TS",
    "EPS_0",
    "ERG",
    "EV",
    "E_CAL",
    "E_TNT",
    "FICHES",
    "FL_OZ",
    "FL_OZ_IMP",
    "FOOT",
    "GAL",
    "GAL_IMP",
    "GAL_US",
    "GAUSS",
    "G_0",
    "G_CONDUCTANCE",
    "G_E",
    "G_F",
    "HA",
    "HBAR",
    "HECTARE",
    "HOUR",
    "H_0",
    "INCH",
    "KB",
    "KN",
    "K_CD",
    "K_J",
    "LB_AV",
    "LITRE",
    "MILE",
    "MIN",
    "MU_0",
    "MU_B",
    "MU_N",
    "MX",
    "M_C12",
    "M_E",
    "M_EVC2",
    "M_N",
    "M_P",
    "M_U",
    "M_W",
    "M_W_S_M_Z",
    "NA",
    "NM",
    "NU_CD",
    "OE",
    "OZ_AV",
    "PC",
    "PHI_0",
    "PHOT",
    "POISE",
    "RAD_MIN",
    "RAD_SEC",
    "RYDBERG",
    "R_E",
    "R_GP",
    "R_K",
    "SIGMA",
    "SIGMA_E",
    "STATC",
    "STILB",
    "STOKES",
    "T0",
    "TON",
    "TORR",
    "UA",
    "YARD",
    "YEAR",
    "YEAR_JULIAN",
    "YEAR_SIDERAL",
    "YEAR_TROPIC",
    "Z_VIDE",
    "C",
    "E",
    "F",
    "Fiche",
    "G",
    "GM_earth",
    "GM_sun",
    "H",
    "L_p",
    "L_sun",
    "M_earth",
    "M_moon",
    "M_p",
    "M_sun",
    "Q_p",
    "R_earth",
    "R_moon",
    "R_sun",
    "S_sun",
    "T_p",
    "T_sun",
    "codata",
    "decrire",
    "e_earth",
    "e_moon",
    "f_earth",
    "mmHG",
    "t_p",
]

_version = tuple(int(n) for n in scipy.__version__.split(".")[:2])
if _version < (1, 15):  # pragma: no cover - dépend de l'environnement
    raise ImportError(
        f"grandeurs.constantes exige scipy ≥ 1.15 (CODATA 2022) ; scipy {scipy.__version__} "
        "fournit CODATA 2018 et donnerait d'autres valeurs. Mettre scipy à jour : "
        'python -m pip install "scipy>=1.15"'
    )


@dataclass(frozen=True, slots=True)
class Fiche:
    """Ce qu'on sait d'une constante : description, source et valeur."""

    nom: str
    description: str
    source: str
    grandeur: Grandeur


FICHES: dict[str, Fiche] = {}

_CODATA = "CODATA 2022, par scipy.constants"
_SI_EXACT = "SI, brochure du BIPM, 9e édition (2019) : valeur exacte par définition"
_SI_USAGE = "brochure SI du BIPM, 9e édition (2019), tableau 8 : unité en usage avec le SI"
_SI_AUTRES = "brochure SI du BIPM, 8e édition (2006), tableau 8 : autre unité hors SI"
_CGS = "brochure SI du BIPM, 8e édition (2006), tableau 9 : unité CGS"
_US = "accord international de 1959 sur le yard et la livre ; NIST Handbook 44, annexe C"
_UAI_2015_B3 = "UAI 2015, résolution B3 : valeur nominale (exacte par convention)"
_LUNE_NASA = "NASA NSSDC, « Moon Fact Sheet »"
_STANDISH = (
    "E. M. Standish, JPL SSD, « Approximate Positions of the Planets », table 1 "
    "(1800-2050), barycentre Terre-Lune"
)


def _noter(nom: str, valeur: Grandeur, description: str, source: str) -> Grandeur:
    FICHES[nom] = Fiche(nom, description, source, valeur)
    return valeur


def codata(cle: str) -> Grandeur:
    """Constante CODATA de scipy, sous la clé anglaise de scipy, en grandeur.

    >>> codata("proton-electron mass ratio")
    """
    valeur, unite, incertitude = physical_constants[cle]
    magnitude = ufloat(valeur, incertitude, tag=cle) if incertitude else valeur
    return ureg.Quantity(magnitude, unite)  # type: ignore[no-any-return]


def _codata(nom: str, cle: str, description: str) -> Grandeur:
    return _noter(nom, codata(cle), description, f"{_CODATA}, « {cle} »")


def _exacte(nom: str, valeur: float, unite: str, description: str, source: str) -> Grandeur:
    return _noter(nom, ureg.Quantity(valeur, unite), description, source)


def _mesuree(
    nom: str, valeur: float, incertitude: float, unite: str, description: str, source: str
) -> Grandeur:
    grandeur = ureg.Quantity(ufloat(valeur, incertitude, tag=nom), unite)
    return _noter(nom, grandeur, description, source)


def _deduite(nom: str, valeur: Any, description: str, source: str) -> Grandeur:
    return _noter(nom, valeur, description, source)


def decrire(nom: str) -> str:
    """Description, valeur et source d'une constante, sur une ligne."""
    fiche = FICHES[nom]
    return f"{nom} = {fiche.grandeur} : {fiche.description} ({fiche.source})"


# Constantes du SI (exactes)

C = _codata("C", "speed of light in vacuum", "vitesse de la lumière dans le vide")
H = _codata("H", "Planck constant", "constante de Planck")
HBAR = _codata("HBAR", "reduced Planck constant", "constante de Planck réduite h/2π")
E = _codata("E", "elementary charge", "charge élémentaire")
KB = _codata("KB", "Boltzmann constant", "constante de Boltzmann")
NA = _codata("NA", "Avogadro constant", "constante d'Avogadro")
DELTA_NU_CS = _codata(
    "DELTA_NU_CS",
    "hyperfine transition frequency of Cs-133",
    "fréquence de la transition hyperfine du césium 133",
)
K_CD = _codata("K_CD", "luminous efficacy", "efficacité lumineuse du rayonnement à 540 THz")
NU_CD = _exacte("NU_CD", 540e12, "Hz", "fréquence du rayonnement qui définit la candela", _SI_EXACT)
CD = _exacte(
    "CD",
    1 / 683,
    "W/sr",
    "intensité énergétique d'une source de 1 cd à 540 THz (définition de la candela)",
    _SI_EXACT,
)

# Constantes qui s'en déduisent exactement

R_GP = _codata("R_GP", "molar gas constant", "constante des gaz parfaits N_A k")
F = _codata("F", "Faraday constant", "constante de Faraday N_A e")
K_J = _codata("K_J", "Josephson constant", "constante de Josephson 2e/h")
R_K = _codata("R_K", "von Klitzing constant", "constante de von Klitzing h/e²")
G_CONDUCTANCE = _codata("G_CONDUCTANCE", "conductance quantum", "quantum de conductance 2e²/h")
PHI_0 = _codata("PHI_0", "mag. flux quantum", "quantum de flux magnétique h/2e")
SIGMA = _codata("SIGMA", "Stefan-Boltzmann constant", "constante de Stefan-Boltzmann")

# Interactions (mesurées)

G = _codata("G", "Newtonian constant of gravitation", "constante de gravitation")
EPS_0 = _codata("EPS_0", "vacuum electric permittivity", "permittivité diélectrique du vide")
MU_0 = _codata("MU_0", "vacuum mag. permeability", "perméabilité magnétique du vide")
ALPHA = _codata("ALPHA", "fine-structure constant", "constante de structure fine")
Z_VIDE = _codata("Z_VIDE", "characteristic impedance of vacuum", "impédance du vide")
G_E = _codata("G_E", "electron g factor", "facteur de Landé de l'électron")
G_F = _deduite(
    "G_F",
    (codata("Fermi coupling constant") * (HBAR * C) ** 3).to("J*m^3"),
    "constante de couplage de Fermi G_F (et non G_F/(ħc)³)",
    f"{_CODATA}, « Fermi coupling constant » × (ħc)³",
)

# Unités de Planck

L_p = _codata("L_p", "Planck length", "longueur de Planck")
M_p = _codata("M_p", "Planck mass", "masse de Planck")
t_p = _codata("t_p", "Planck time", "temps de Planck")
T_p = _codata("T_p", "Planck temperature", "température de Planck M_p c²/k")
Q_p = _deduite(
    "Q_p",
    ((4 * math.pi * EPS_0 * HBAR * C) ** 0.5).to("C"),
    "charge de Planck √(4π ε₀ ħ c)",
    f"calculée d'après {_CODATA}",
)

# Particules

M_E = _codata("M_E", "electron mass", "masse de l'électron")
M_P = _codata("M_P", "proton mass", "masse du proton")
M_N = _codata("M_N", "neutron mass", "masse du neutron")
M_U = _codata("M_U", "atomic mass constant", "constante de masse atomique (1 u)")
DA = _deduite("DA", M_U, "dalton, égal à l'unité de masse atomique", FICHES["M_U"].source)
M_C12 = _codata(
    "M_C12", "molar mass of carbon-12", "masse molaire du carbone 12 (une masse molaire)"
)
M_W = _mesuree(
    "M_W",
    80.3692,
    0.0133,
    "GeV/c^2",
    "masse du boson W",
    "Particle Data Group, Phys. Rev. D 110, 030001 (2024), moyenne mondiale",
)
M_W_S_M_Z = _codata("M_W_S_M_Z", "W to Z mass ratio", "rapport des masses des bosons W et Z")
RYDBERG = _codata("RYDBERG", "Rydberg constant", "constante de Rydberg")
D_0 = _codata("D_0", "quantum of circulation", "quantum de circulation h/2mₑ")
MU_B = _codata("MU_B", "Bohr magneton", "magnéton de Bohr eħ/2mₑ")
MU_N = _codata("MU_N", "nuclear magneton", "magnéton nucléaire eħ/2mₚ")
A_0 = _codata("A_0", "Bohr radius", "rayon de Bohr")
R_E = _codata("R_E", "classical electron radius", "rayon classique de l'électron")
SIGMA_E = _codata("SIGMA_E", "Thomson cross section", "section efficace de Thomson")
HA = _codata("HA", "Hartree energy", "énergie de Hartree")

# Unités de temps, d'angle, de longueur, de surface, de volume, de masse

MIN = _exacte("MIN", 60, "s", "minute", _SI_USAGE)
HOUR = _exacte("HOUR", 3600, "s", "heure", _SI_USAGE)
DAY = _exacte("DAY", 86400, "s", "jour", _SI_USAGE)
YEAR = _exacte("YEAR", 365 * 86400, "s", "année commune de 365 jours", "définition")
DEG = _exacte("DEG", math.pi / 180, "rad", "degré d'angle", _SI_USAGE)
RAD_MIN = _exacte("RAD_MIN", math.pi / 10800, "rad", "minute d'angle", _SI_USAGE)
RAD_SEC = _exacte("RAD_SEC", math.pi / 648000, "rad", "seconde d'angle", _SI_USAGE)
ANGSTROM = _exacte("ANGSTROM", 1e-10, "m", "ångström", _SI_AUTRES)
NM = _exacte("NM", 1852, "m", "mille marin (et non le nanomètre)", _SI_AUTRES)
KN = _exacte("KN", 1852 / 3600, "m/s", "nœud, un mille marin par heure", _SI_AUTRES)
LITRE = _exacte("LITRE", 1e-3, "m^3", "litre", _SI_USAGE)
HECTARE = _exacte("HECTARE", 1e4, "m^2", "hectare", _SI_USAGE)
BARN = _exacte("BARN", 1e-28, "m^2", "barn", _SI_AUTRES)
TON = _exacte("TON", 1000, "kg", "tonne", _SI_USAGE)

# Pression, température, énergie

G_0 = _codata("G_0", "standard acceleration of gravity", "pesanteur normale (3e CGPM, 1901)")
ATM = _codata("ATM", "standard atmosphere", "atmosphère normale")
BAR = _exacte("BAR", 1e5, "Pa", "bar", _SI_AUTRES)
mmHG = _exacte(
    "mmHG",
    133.322387415,
    "Pa",
    "millimètre de mercure conventionnel, 13,5951 g/cm³ × g₀ × 1 mm",
    _SI_AUTRES,
)
TORR = _exacte("TORR", 101325 / 760, "Pa", "torr, 1/760 d'atmosphère normale", "définition")
T0 = _exacte("T0", 273.15, "K", "zéro de l'échelle Celsius", "définition de l'échelle Celsius")
EV = _codata("EV", "electron volt", "électronvolt")
M_EVC2 = _deduite(
    "M_EVC2",
    (EV / C**2).to("kg"),
    "masse équivalente à 1 eV, eV/c²",
    f"calculée d'après {_CODATA}",
)
E_CAL = _exacte("E_CAL", 4.184, "J", "calorie thermochimique", "ISO 80000-5 : 4,184 J exactement")
E_TNT = _exacte(
    "E_TNT", 4.184e9, "J", "tonne d'équivalent TNT", "convention : 10⁹ calories thermochimiques"
)

# Unités anglo-saxonnes

INCH = _exacte("INCH", 0.0254, "m", "pouce", _US)
FOOT = _exacte("FOOT", 0.3048, "m", "pied, 12 pouces", _US)
YARD = _exacte("YARD", 0.9144, "m", "yard, 3 pieds", _US)
MILE = _exacte("MILE", 1609.344, "m", "mile terrestre, 1760 yards", _US)
GAL_US = _exacte("GAL_US", 3.785411784e-3, "m^3", "gallon américain, 231 pouces cubes", _US)
FL_OZ = _exacte("FL_OZ", 3.785411784e-3 / 128, "m^3", "once liquide américaine", _US)
GAL_IMP = _exacte("GAL_IMP", 4.54609e-3, "m^3", "gallon impérial (britannique)", _US)
FL_OZ_IMP = _exacte("FL_OZ_IMP", 4.54609e-3 / 160, "m^3", "once liquide impériale", _US)
LB_AV = _exacte("LB_AV", 0.45359237, "kg", "livre avoirdupois", _US)
OZ_AV = _exacte("OZ_AV", 0.45359237 / 16, "kg", "once avoirdupois", _US)

# Unités CGS

ERG = _exacte("ERG", 1e-7, "J", "erg", _CGS)
DYN = _exacte("DYN", 1e-5, "N", "dyne", _CGS)
POISE = _exacte("POISE", 0.1, "Pa*s", "poise", _CGS)
STOKES = _exacte("STOKES", 1e-4, "m^2/s", "stokes", _CGS)
STILB = _exacte("STILB", 1e4, "cd/m^2", "stilb", _CGS)
PHOT = _exacte("PHOT", 1e4, "lx", "phot", _CGS)
GAL = _exacte("GAL", 1e-2, "m/s^2", "gal (accélération)", _CGS)
MX = _exacte("MX", 1e-8, "Wb", "maxwell", _CGS)
GAUSS = _exacte("GAUSS", 1e-4, "T", "gauss", _CGS)
OE = _exacte("OE", 1000 / (4 * math.pi), "A/m", "œrsted", _CGS)
STATC = _exacte(
    "STATC",
    1 / 2997924580,
    "C",
    "statcoulomb (franklin), unité de charge du système CGS électrostatique",
    "définition CGS-ues : 1 C = 10 c (en cm/s) statC",
)

# Astronomie

UA = _exacte("UA", 149597870700, "m", "unité astronomique", "UAI 2012, résolution B2 (exacte)")
PC = _exacte(
    "PC",
    648000 / math.pi * 149597870700,
    "m",
    "parsec, 648 000/π ua",
    "UAI 2015, résolution B2 (exacte)",
)
YEAR_JULIAN = _exacte(
    "YEAR_JULIAN", 365.25 * 86400, "s", "année julienne, 365,25 j", "UAI (définition)"
)
AL = _exacte(
    "AL",
    299792458 * 365.25 * 86400,
    "m",
    "année-lumière, c × année julienne",
    "UAI (définition)",
)
YEAR_SIDERAL = _exacte(
    "YEAR_SIDERAL",
    365.256363004 * 86400,
    "s",
    "année sidérale, 365,256 363 004 j (J2000)",
    "Astronomical Almanac, glossaire",
)
YEAR_TROPIC = _exacte(
    "YEAR_TROPIC",
    365.24219 * 86400,
    "s",
    "année tropique moyenne, 365,242 19 j (J2000)",
    "J. Laskar, A&A 157, 59 (1986), arrondi",
)
H_0 = _mesuree(
    "H_0",
    67.4,
    0.5,
    "km/s/Mpc",
    "constante de Hubble (les mesures locales donnent 73 km/s/Mpc : « tension de Hubble »)",
    "Planck Collaboration, A&A 641, A6 (2020)",
)
GM_sun = _exacte(
    "GM_sun", 1.3271244e20, "m^3/s^2", "paramètre gravitationnel du Soleil", _UAI_2015_B3
)
M_sun = _deduite(
    "M_sun", (GM_sun / G).to("kg"), "masse du Soleil, (GM)☉/G", f"{_UAI_2015_B3} ; G {_CODATA}"
)
R_sun = _exacte("R_sun", 6.957e8, "m", "rayon du Soleil", _UAI_2015_B3)
L_sun = _exacte("L_sun", 3.828e26, "W", "luminosité du Soleil", _UAI_2015_B3)
S_sun = _exacte("S_sun", 1361, "W/m^2", "éclairement solaire total à 1 ua", _UAI_2015_B3)
T_sun = _exacte("T_sun", 5772, "K", "température effective du Soleil", _UAI_2015_B3)
GM_earth = _exacte(
    "GM_earth", 3.986004e14, "m^3/s^2", "paramètre gravitationnel de la Terre", _UAI_2015_B3
)
M_earth = _deduite(
    "M_earth",
    (GM_earth / G).to("kg"),
    "masse de la Terre, (GM)⊕/G",
    f"{_UAI_2015_B3} ; G {_CODATA}",
)
R_earth = _exacte(
    "R_earth",
    6378137,
    "m",
    "rayon équatorial de la Terre (demi-grand axe de l'ellipsoïde)",
    "WGS 84, NGA.STND.0036 (2014) : paramètre de définition",
)
f_earth = _exacte(
    "f_earth",
    1 / 298.257223563,
    "",
    "aplatissement de l'ellipsoïde terrestre",
    "WGS 84, NGA.STND.0036 (2014) : paramètre de définition",
)
e_earth = _exacte("e_earth", 0.01671123, "", "excentricité de l'orbite terrestre", _STANDISH)
D_TS = _exacte(
    "D_TS",
    1.00000261 * 149597870700,
    "m",
    "demi-grand axe de l'orbite terrestre, 1,000 002 61 ua",
    _STANDISH,
)
M_moon = _deduite(
    "M_moon",
    M_earth * 0.0123000371,
    "masse de la Lune, M⊕ × 0,012 300 0371",
    "rapport des masses UAI 2009 (Luzum et al., Celest. Mech. Dyn. Astron. 110, 293, 2011)",
)
R_moon = _exacte(
    "R_moon",
    1.7374e6,
    "m",
    "rayon moyen de la Lune",
    "UAI, groupe WGCCRE (Archinal et al., Celest. Mech. Dyn. Astron. 130, 22, 2018)",
)
D_TL = _exacte(
    "D_TL", 3.84399e8, "m", "demi-grand axe de l'orbite lunaire", f"{_LUNE_NASA} (0,3844 Gm)"
)
e_moon = _exacte("e_moon", 0.0549, "", "excentricité de l'orbite lunaire", _LUNE_NASA)
