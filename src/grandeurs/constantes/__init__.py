"""Constantes physiques et unités hors SI, en grandeurs.

Chaque constante est une :class:`grandeurs.Grandeur` : valeur, incertitude-type
(un ``ufloat`` quand elle n'est pas nulle) et unité. La même liste existe en
simples flottants SI dans :mod:`grandeurs.flottants`, pour les calculs qui
n'utilisent pas d'unités.

Ce module donne les constantes fondamentales et les unités en usage avec le
SI ; trois sous-modules donnent le reste, pour que ces noms ne masquent rien
dans un ``from grandeurs.constantes import *`` :

- :mod:`grandeurs.constantes.astro` : constantes astronomiques (UAI), Terre, Lune ;
- :mod:`grandeurs.constantes.cgs` : unités du système CGS ;
- :mod:`grandeurs.constantes.us` : unités anglo-saxonnes.

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
mass ratio")``), et :func:`cles_codata` liste les clés.

Noms : ceux de l'ancien paquet ``constantes``, sauf les cinq qu'un physicien
lisait de travers : ``HARTREE`` (et non ``HA``, un hectare), ``G_N`` (et non
``G_0``, un quantum de conductance), ``NOEUD`` (et non ``KN``, un kilonewton),
``MILLE_MARIN`` (et non ``NM``, un nanomètre), ``GAL_CGS`` (et non ``GAL``, un
gallon). Les huit noms que les corrigés emploient (``R_GP``, ``NA``, ``E``,
``M_E``, ``EPS_0``, ``HBAR``, ``H``, ``C``) sont inchangés.
"""

import math

from grandeurs.constantes._fiches import (
    CODATA,
    FICHES,
    SI_AUTRES,
    SI_EXACT,
    SI_USAGE,
    Fiche,
    cles_codata,
    codata,
    codata_notee,
    decrire,
    deduite,
    exacte,
    mesuree,
)

__all__ = [
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
    "D_0",
    "EPS_0",
    "EV",
    "E_CAL",
    "E_TNT",
    "FICHES",
    "G_CONDUCTANCE",
    "G_E",
    "G_F",
    "G_N",
    "HARTREE",
    "HBAR",
    "HECTARE",
    "HOUR",
    "KB",
    "K_CD",
    "K_J",
    "LITRE",
    "MILLE_MARIN",
    "MIN",
    "MU_0",
    "MU_B",
    "MU_N",
    "M_C12",
    "M_E",
    "M_EVC2",
    "M_N",
    "M_P",
    "M_U",
    "M_W",
    "M_W_S_M_Z",
    "NA",
    "NOEUD",
    "NU_CD",
    "PHI_0",
    "RAD_MIN",
    "RAD_SEC",
    "RYDBERG",
    "R_E",
    "R_GP",
    "R_K",
    "SIGMA",
    "SIGMA_E",
    "T0",
    "TON",
    "TORR",
    "YEAR",
    "Z_VIDE",
    "C",
    "E",
    "F",
    "Fiche",
    "G",
    "H",
    "L_p",
    "M_p",
    "Q_p",
    "T_p",
    "cles_codata",
    "codata",
    "decrire",
    "mmHG",
    "t_p",
]

# Constantes du SI (exactes)

C = codata_notee("C", "speed of light in vacuum", "vitesse de la lumière dans le vide")
H = codata_notee("H", "Planck constant", "constante de Planck")
HBAR = codata_notee("HBAR", "reduced Planck constant", "constante de Planck réduite h/2π")
E = codata_notee("E", "elementary charge", "charge élémentaire")
KB = codata_notee("KB", "Boltzmann constant", "constante de Boltzmann")
NA = codata_notee("NA", "Avogadro constant", "constante d'Avogadro")
DELTA_NU_CS = codata_notee(
    "DELTA_NU_CS",
    "hyperfine transition frequency of Cs-133",
    "fréquence de la transition hyperfine du césium 133",
)
K_CD = codata_notee("K_CD", "luminous efficacy", "efficacité lumineuse du rayonnement à 540 THz")
NU_CD = exacte("NU_CD", 540e12, "Hz", "fréquence du rayonnement qui définit la candela", SI_EXACT)
CD = exacte(
    "CD",
    1 / 683,
    "W/sr",
    "intensité énergétique d'une source de 1 cd à 540 THz (définition de la candela)",
    SI_EXACT,
)

# Constantes qui s'en déduisent exactement

R_GP = codata_notee("R_GP", "molar gas constant", "constante des gaz parfaits N_A k")
F = codata_notee("F", "Faraday constant", "constante de Faraday N_A e")
K_J = codata_notee("K_J", "Josephson constant", "constante de Josephson 2e/h")
R_K = codata_notee("R_K", "von Klitzing constant", "constante de von Klitzing h/e²")
G_CONDUCTANCE = codata_notee("G_CONDUCTANCE", "conductance quantum", "quantum de conductance 2e²/h")
PHI_0 = codata_notee("PHI_0", "mag. flux quantum", "quantum de flux magnétique h/2e")
SIGMA = codata_notee("SIGMA", "Stefan-Boltzmann constant", "constante de Stefan-Boltzmann")

# Interactions (mesurées)

G = codata_notee("G", "Newtonian constant of gravitation", "constante de gravitation")
EPS_0 = codata_notee("EPS_0", "vacuum electric permittivity", "permittivité diélectrique du vide")
MU_0 = codata_notee("MU_0", "vacuum mag. permeability", "perméabilité magnétique du vide")
ALPHA = codata_notee("ALPHA", "fine-structure constant", "constante de structure fine")
Z_VIDE = codata_notee("Z_VIDE", "characteristic impedance of vacuum", "impédance du vide")
G_E = codata_notee("G_E", "electron g factor", "facteur de Landé de l'électron")
G_F = deduite(
    "G_F",
    (codata("Fermi coupling constant") * (HBAR * C) ** 3).to("J*m^3"),
    "constante de couplage de Fermi G_F (et non G_F/(ħc)³)",
    f"{CODATA}, « Fermi coupling constant » × (ħc)³",
)

# Unités de Planck

L_p = codata_notee("L_p", "Planck length", "longueur de Planck")
M_p = codata_notee("M_p", "Planck mass", "masse de Planck")
t_p = codata_notee("t_p", "Planck time", "temps de Planck")
T_p = codata_notee("T_p", "Planck temperature", "température de Planck M_p c²/k")
Q_p = deduite(
    "Q_p",
    ((4 * math.pi * EPS_0 * HBAR * C) ** 0.5).to("C"),
    "charge de Planck √(4π ε₀ ħ c)",
    f"calculée d'après {CODATA}",
)

# Particules

M_E = codata_notee("M_E", "electron mass", "masse de l'électron")
M_P = codata_notee("M_P", "proton mass", "masse du proton")
M_N = codata_notee("M_N", "neutron mass", "masse du neutron")
M_U = codata_notee("M_U", "atomic mass constant", "constante de masse atomique (1 u)")
DA = deduite("DA", M_U, "dalton, égal à l'unité de masse atomique", FICHES["M_U"].source)
M_C12 = codata_notee(
    "M_C12", "molar mass of carbon-12", "masse molaire du carbone 12 (une masse molaire)"
)
M_W = mesuree(
    "M_W",
    80.3692,
    0.0133,
    "GeV/c^2",
    "masse du boson W",
    "Particle Data Group, Phys. Rev. D 110, 030001 (2024), moyenne mondiale",
)
M_W_S_M_Z = codata_notee("M_W_S_M_Z", "W to Z mass ratio", "rapport des masses des bosons W et Z")
RYDBERG = codata_notee("RYDBERG", "Rydberg constant", "constante de Rydberg")
D_0 = codata_notee("D_0", "quantum of circulation", "quantum de circulation h/2mₑ")
MU_B = codata_notee("MU_B", "Bohr magneton", "magnéton de Bohr eħ/2mₑ")
MU_N = codata_notee("MU_N", "nuclear magneton", "magnéton nucléaire eħ/2mₚ")
A_0 = codata_notee("A_0", "Bohr radius", "rayon de Bohr")
R_E = codata_notee("R_E", "classical electron radius", "rayon classique de l'électron")
SIGMA_E = codata_notee("SIGMA_E", "Thomson cross section", "section efficace de Thomson")
HARTREE = codata_notee("HARTREE", "Hartree energy", "énergie de Hartree")

# Unités de temps, d'angle, de longueur, de surface, de volume, de masse

MIN = exacte("MIN", 60, "s", "minute", SI_USAGE)
HOUR = exacte("HOUR", 3600, "s", "heure", SI_USAGE)
DAY = exacte("DAY", 86400, "s", "jour", SI_USAGE)
YEAR = exacte("YEAR", 365 * 86400, "s", "année commune de 365 jours", "définition")
DEG = exacte("DEG", math.pi / 180, "rad", "degré d'angle", SI_USAGE)
RAD_MIN = exacte("RAD_MIN", math.pi / 10800, "rad", "minute d'angle", SI_USAGE)
RAD_SEC = exacte("RAD_SEC", math.pi / 648000, "rad", "seconde d'angle", SI_USAGE)
ANGSTROM = exacte("ANGSTROM", 1e-10, "m", "ångström", SI_AUTRES)
MILLE_MARIN = exacte("MILLE_MARIN", 1852, "m", "mille marin", SI_AUTRES)
NOEUD = exacte("NOEUD", 1852 / 3600, "m/s", "nœud, un mille marin par heure", SI_AUTRES)
LITRE = exacte("LITRE", 1e-3, "m^3", "litre", SI_USAGE)
HECTARE = exacte("HECTARE", 1e4, "m^2", "hectare", SI_USAGE)
BARN = exacte("BARN", 1e-28, "m^2", "barn", SI_AUTRES)
TON = exacte("TON", 1000, "kg", "tonne", SI_USAGE)

# Pression, température, énergie

G_N = codata_notee("G_N", "standard acceleration of gravity", "pesanteur normale (3e CGPM, 1901)")
ATM = codata_notee("ATM", "standard atmosphere", "atmosphère normale")
BAR = exacte("BAR", 1e5, "Pa", "bar", SI_AUTRES)
mmHG = exacte(
    "mmHG",
    133.322387415,
    "Pa",
    "millimètre de mercure conventionnel, 13,5951 g/cm³ × g₀ × 1 mm",
    SI_AUTRES,
)
TORR = exacte("TORR", 101325 / 760, "Pa", "torr, 1/760 d'atmosphère normale", "définition")
T0 = exacte("T0", 273.15, "K", "zéro de l'échelle Celsius", "définition de l'échelle Celsius")
EV = codata_notee("EV", "electron volt", "électronvolt")
M_EVC2 = deduite(
    "M_EVC2",
    (EV / C**2).to("kg"),
    "masse équivalente à 1 eV, eV/c²",
    f"calculée d'après {CODATA}",
)
E_CAL = exacte("E_CAL", 4.184, "J", "calorie thermochimique", "ISO 80000-5 : 4,184 J exactement")
E_TNT = exacte(
    "E_TNT", 4.184e9, "J", "tonne d'équivalent TNT", "convention : 10⁹ calories thermochimiques"
)

# Les sous-modules sont chargés en dernier : ils s'appuient sur G et C, et FICHES
# recense ainsi tout dès `import grandeurs.constantes`.
from grandeurs.constantes import astro, cgs, us  # noqa: E402, F401
