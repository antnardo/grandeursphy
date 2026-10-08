"""Les constantes de :mod:`grandeurs.constantes` en simples flottants SI.

Les corrigés existants calculent en flottants (``R_GP * T``) et formatent le
résultat (``f"{x:.3e}"``) ; une grandeur y changerait le type du résultat et
son écriture. Ce module leur donne les mêmes noms qu'avant, en ``float``,
valeur centrale exprimée en unités SI de base (kg, m, s, A, K, mol, cd ; le
radian pour les angles) : ``from grandeurs.flottants import R_GP``.

Les valeurs viennent des grandeurs de :mod:`grandeurs.constantes`, si bien que
les deux modules ne peuvent pas diverger. Les constantes exactes (c, h, e, k,
N_A et ce qui s'en déduit : ħ, R…) ont les mêmes flottants qu'avec CODATA 2018 ;
les constantes mesurées (ε₀, mₑ, G…) ont leur valeur CODATA 2022.
"""

from typing import Any

from grandeurs import constantes as _c

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
    "e_earth",
    "e_moon",
    "f_earth",
    "mmHG",
    "t_p",
]


def _si(grandeur: Any) -> float:
    return float(grandeur.valeur_si)


C = _si(_c.C)
H = _si(_c.H)
HBAR = _si(_c.HBAR)
E = _si(_c.E)
KB = _si(_c.KB)
NA = _si(_c.NA)
DELTA_NU_CS = _si(_c.DELTA_NU_CS)
K_CD = _si(_c.K_CD)
NU_CD = _si(_c.NU_CD)
CD = _si(_c.CD)
R_GP = _si(_c.R_GP)
F = _si(_c.F)
K_J = _si(_c.K_J)
R_K = _si(_c.R_K)
G_CONDUCTANCE = _si(_c.G_CONDUCTANCE)
PHI_0 = _si(_c.PHI_0)
SIGMA = _si(_c.SIGMA)
G = _si(_c.G)
EPS_0 = _si(_c.EPS_0)
MU_0 = _si(_c.MU_0)
ALPHA = _si(_c.ALPHA)
Z_VIDE = _si(_c.Z_VIDE)
G_E = _si(_c.G_E)
G_F = _si(_c.G_F)
L_p = _si(_c.L_p)
M_p = _si(_c.M_p)
t_p = _si(_c.t_p)
T_p = _si(_c.T_p)
Q_p = _si(_c.Q_p)
M_E = _si(_c.M_E)
M_P = _si(_c.M_P)
M_N = _si(_c.M_N)
M_U = _si(_c.M_U)
DA = _si(_c.DA)
M_C12 = _si(_c.M_C12)
M_W = _si(_c.M_W)
M_W_S_M_Z = _si(_c.M_W_S_M_Z)
RYDBERG = _si(_c.RYDBERG)
D_0 = _si(_c.D_0)
MU_B = _si(_c.MU_B)
MU_N = _si(_c.MU_N)
A_0 = _si(_c.A_0)
R_E = _si(_c.R_E)
SIGMA_E = _si(_c.SIGMA_E)
HA = _si(_c.HA)
MIN = _si(_c.MIN)
HOUR = _si(_c.HOUR)
DAY = _si(_c.DAY)
YEAR = _si(_c.YEAR)
DEG = _si(_c.DEG)
RAD_MIN = _si(_c.RAD_MIN)
RAD_SEC = _si(_c.RAD_SEC)
ANGSTROM = _si(_c.ANGSTROM)
NM = _si(_c.NM)
KN = _si(_c.KN)
LITRE = _si(_c.LITRE)
HECTARE = _si(_c.HECTARE)
BARN = _si(_c.BARN)
TON = _si(_c.TON)
G_0 = _si(_c.G_0)
ATM = _si(_c.ATM)
BAR = _si(_c.BAR)
mmHG = _si(_c.mmHG)
TORR = _si(_c.TORR)
T0 = _si(_c.T0)
EV = _si(_c.EV)
M_EVC2 = _si(_c.M_EVC2)
E_CAL = _si(_c.E_CAL)
E_TNT = _si(_c.E_TNT)
INCH = _si(_c.INCH)
FOOT = _si(_c.FOOT)
YARD = _si(_c.YARD)
MILE = _si(_c.MILE)
GAL_US = _si(_c.GAL_US)
FL_OZ = _si(_c.FL_OZ)
GAL_IMP = _si(_c.GAL_IMP)
FL_OZ_IMP = _si(_c.FL_OZ_IMP)
LB_AV = _si(_c.LB_AV)
OZ_AV = _si(_c.OZ_AV)
ERG = _si(_c.ERG)
DYN = _si(_c.DYN)
POISE = _si(_c.POISE)
STOKES = _si(_c.STOKES)
STILB = _si(_c.STILB)
PHOT = _si(_c.PHOT)
GAL = _si(_c.GAL)
MX = _si(_c.MX)
GAUSS = _si(_c.GAUSS)
OE = _si(_c.OE)
STATC = _si(_c.STATC)
UA = _si(_c.UA)
PC = _si(_c.PC)
YEAR_JULIAN = _si(_c.YEAR_JULIAN)
AL = _si(_c.AL)
YEAR_SIDERAL = _si(_c.YEAR_SIDERAL)
YEAR_TROPIC = _si(_c.YEAR_TROPIC)
H_0 = _si(_c.H_0)
GM_sun = _si(_c.GM_sun)
M_sun = _si(_c.M_sun)
R_sun = _si(_c.R_sun)
L_sun = _si(_c.L_sun)
S_sun = _si(_c.S_sun)
T_sun = _si(_c.T_sun)
GM_earth = _si(_c.GM_earth)
M_earth = _si(_c.M_earth)
R_earth = _si(_c.R_earth)
f_earth = _si(_c.f_earth)
e_earth = _si(_c.e_earth)
D_TS = _si(_c.D_TS)
M_moon = _si(_c.M_moon)
R_moon = _si(_c.R_moon)
D_TL = _si(_c.D_TL)
e_moon = _si(_c.e_moon)
