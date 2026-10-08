from units import UNIT_L, UNIT_M, UNIT_K as UNIT_T
from units import Unit

UNIT_P = Unit(symbole='P', SI='Pa', conversions={'bar': 1e5})
UNIT_E = Unit(symbole='H', SI='J')
UNIT_V = UNIT_L**3
UNIT_V.set_symbole('V')
UNIT_v = UNIT_V/UNIT_M
UNIT_v.set_symbole('v')
UNIT_S = UNIT_E/UNIT_T/UNIT_M
UNIT_S.set_symbole("S")
UNIT_H = UNIT_E/UNIT_M
UNIT_H.set_symbole("H")

print(UNIT_P)
print(UNIT_P(1, 'Pa'))
print(UNIT_P(1, 'bar'))
print(UNIT_P(1, 'kPa'))
UNIT_P.set_default('bar')
print(UNIT_P(1, 'bar'))
print(UNIT_P(1, 'kPa', verbose=True))
print(UNIT_T)
print(UNIT_T(10, 'K'))
print(UNIT_T(10, '°C'))
UNIT_T.set_default('°C')
print(UNIT_T(10, 'K'))
print(UNIT_T(10, '°C'))
print(UNIT_E)
print(UNIT_M)
print(UNIT_M(1, 'g'))
print(UNIT_M(1, 'kg'))
print(UNIT_M(1, 'Mg'))
print(UNIT_L)
print(UNIT_L.latex)

print(UNIT_V)
print(UNIT_v)
print(UNIT_v.latex)
print(UNIT_S)
print(UNIT_H)
print(UNIT_H(1, 'kJ/g'))
