from .pi import pi
from decimal import Decimal

# CGS
ERG = Decimal(1)/10**7  # J
DYN = Decimal(1)/10**5  # N
POISE = Decimal(1)/10**1  # Pa.s
STOKES = Decimal(1)/10**4  # m^2/s
STILB = Decimal(1)*10**4  # cd/m^2
PHOT = Decimal(1)*10**4  # lx
GAL = Decimal(1)/10**2  # m/s^2
MX = Decimal(1)/10**8  # Wb (Maxwell)
GAUSS = Decimal(1)/10**4  # T
OE = Decimal(1)*10**3/(4*pi())  # Oersted (T)
