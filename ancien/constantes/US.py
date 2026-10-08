from decimal import Decimal

# Unités anglosaxonnes
INCH = Decimal(254)/1000
FOOT = 12*INCH
YARD = 3*FOOT
MILE = 1760*YARD  # 1760 verges, de 3 pieds
GAL = Decimal(3_785_411_784)/10**9  # galon, m^3
FL_OZ = GAL/128  # once liquide
GAL_IMP = Decimal(4_546_09)/10**8  # UK !
FL_OZ_IMP = GAL_IMP/160
LB_AV = Decimal(453_592_37)/10**8  # livre - kg
OZ_AV = LB_AV/16  # once

__CONSTANTES_US__ = [
    'INCH', 'FOOT', 'YARD', 'MILE',
    'GAL', 'FL_OZ', 'GAL_IMP', 'FL_OZ_IMP',
    'LB_AV', 'OZ_AV'
]