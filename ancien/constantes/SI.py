from constantes.pi import pi
from constantes.dataclass import Decimal

# SI
C = Decimal(299_792_458)
KB = Decimal(1380649)/10**29
NA = Decimal(602214076)*10**15
H = Decimal(662607015)/10**42
E = Decimal(1602176634)/10**28
# fréquence de transition de 133 Cs (Hz)
DELTA_NU_CS = Decimal(9_192_631_770)
# rayonnement monochromatique de référence
K_CD = Decimal(540)*10**12  # (Hz)
CD = K_CD/683  # kg/m^2/s^3/sr

# Constantes dérivées exactes

R_GP = KB*NA
HBAR = H/(2*pi())
# cte de Josephson (Hz/V)
K_J = 2*E/H
# cte de Faraday (C/mol)
F = NA*E
# cte de Stefan (W/m^2/K^4)
SIGMA = pi()**2*KB**4/(60*HBAR**3*C**2)
# cte de Von Klitzing (ohm)
R_K = H/E**2
# Quantum de conductance (S)
G_0 = 2*E**2/H
# Quantum de flux magnétique (Wb)
PHI_0 = H/(2*E)
