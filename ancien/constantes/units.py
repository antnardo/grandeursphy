from .pi import pi
from decimal import Decimal
from .SI import E, C

# Définitions unités

# Time
MIN = Decimal(60)
HOUR = 60*MIN
DAY = 24*HOUR
YEAR = 365*DAY

# Angles
DEG = pi()/180
RAD_MIN = DEG/60
RAD_SEC = DEG/3600

# Longueur
ANGSTROM = Decimal(1)/10**10
NM = Decimal(1_852)  # Mille nautique

# Vitesses
KN = NM/3600  # Noeud

# Volume
LITRE = Decimal(1)/1000

# Surface
HA = Decimal(10000)  # hectare
BARN = Decimal(1)/10**28  # m^2

# Masse
TON = Decimal(1000)
# Unité de masse atomique unifiée (kg)
M_U = Decimal(1_660_539_066_60)/10**38  # 1/12 de la masse de C^12 ± (50) (mal définie)
DA = M_U  # dalton (kg)

# pesanteur (m/s^2)
G_0 = Decimal(9_806_65)/10**5

# atmosphère (Pa)
ATM = Decimal(1_01325)
BAR = Decimal(100_000)
mmHG = ATM/760

# Température celsius (K)
T0 = Decimal(273_16)/100


# Energies
# electron volt (J)
EV = E
# Masse énergie
M_EVC2 = EV/C**2
# CALORIE
E_CAL = Decimal(4_184)/1000
# TNT
E_TNT = 10**9*E_CAL
