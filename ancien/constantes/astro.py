from .pi import pi
from decimal import Decimal
from .SI import C

# Astro
# Unité astronomique (m)
UA = Decimal(149_597_870_700)
# Parsec
PC = Decimal(648_000)/pi()*UA
# Année julienne (s)
YEAR_JULIAN = Decimal(31_557_600)
# Année lumière (m)
AL = C*YEAR_JULIAN


YEAR_SIDERAL = Decimal(31_558_149_8)/10
YEAR_TROPIC = Decimal(31_556_925_2)/10


H_0 = Decimal('69.32e-3')/PC  # Hubble (WMAP 2012) ± 0,80

M_sun = Decimal('1.9884e30')  # ± (30)
R_sun = Decimal('696.1e6')
L_sun = Decimal('384.6e24')  # W ± (8)
M_earth = Decimal('5.9723e24')  # ± (9)
R_earth = Decimal('6_378_137')  # équatorial
# Aplatissement de l'ellipsoide terrestre
f_earth = Decimal('3.352_836e-3')
e_earth = Decimal('0.01671022')
D_TS = Decimal('149_597_887.5e3')  # demi grand axe
M_moon = Decimal('7.3477e22')
R_moon = Decimal('1.7374e3')  # équatorial
D_TL = Decimal('384_399e3')  # demi grand axe
e_moon = Decimal('0.05490')
