from .pi import pi
from decimal import Decimal
from .SI import E, H, C, HBAR
from .units import EV

# Mesurées
# cte de graviation (m^3/kg^-1.s^-2)
G = Decimal('6.67408e-11')  # ± (31)
EPS_0 = Decimal('8.8541878128e-12')  # ± (13)
# MU_0 = Decimal('1.25663706212e-6')  # ± (19)
MU_0 = 1/C**2/EPS_0

# cte de structure fine
ALPHA = E**2/(2*EPS_0*H*C)

# impédance du vide (ohm)
Z_VIDE = MU_0*C

# Facteur de Landé de l'électron
G_E = Decimal('-2.002_319_304_362_56')  # ± 35
# Constante de couplage de Fermi
G_F = Decimal('1.166_378_7e-5')/(10**9*EV)**2*(HBAR*C)**3  # ± (7)


# AUTRES UNITES DERIVEES
# Plancks units
# longueur de planck
L_p = (HBAR*G/C**3).sqrt()
# masse de planck
M_p = (HBAR*C/G).sqrt()
# temps de planck
t_p = L_p/C
# charge de planck
Q_p = (4*pi()*EPS_0*HBAR*C).sqrt()
