from .pi import pi
from decimal import Decimal
from .SI import H, HBAR, E, C, KB
from .interactions import EPS_0, ALPHA
from .units import M_EVC2

M_E = Decimal('9.1093837015e-31')  # ± (28)
M_P = Decimal('1.67262192369e-27')  # ± (51)
M_N = Decimal('1.67492749804e-27')  # ± (95)
M_C12 = Decimal('11.9999999958e-3')  # ± (36)
# Masse boson
M_W = Decimal('80.403e9')*M_EVC2  # ± (29)
# Rapport des masses des bosons - angle de Weinberg
M_W_S_M_Z = Decimal('0.881_53')  # ± (17)

# Constantes dérivées liées au particules

# cte de rydbgerg (m^-1)
RYDBERG = ALPHA**2*M_E*C/(2*H)

# Quantum de circulation (m^2/s)
D_0 = H/(2*M_E)

# Magnéton de Bohr (J/T)
MU_B = E*HBAR/(2*M_E)

# Magnéton nucléaire (J/T)
MU_N = E*HBAR/(2*M_N)

# Rayon de Bohr
A_0 = HBAR/(ALPHA*M_E*C)

# Rayon de l'electron classique
R_E = E**2/(4*pi()*EPS_0*M_E*C**2)

# Section efficace de Thomson
SIGMA_E = (8*pi()/3)*R_E**2

# Energie de Hartree
HA = 2*RYDBERG*H*C

# température de planck
T_p = M_P*C**2/KB
