from units.classes import Unit

UNIT_K = Unit(symbole='T', SI='K', conversions={'°C': lambda x: x+273.15},
              inverse_conversions={'°C': lambda x: x-273.15})
UNIT_M = Unit(symbole='m', SI='kg', collapse=True)
UNIT_L = Unit(symbole='L', SI='m')
UNIT_T = Unit(symbole='t', SI='s', conversions={'j': 86400, 'js': 86164, 'a': 86400*365.2422, 'h': 3600, 'min': 60})
UNIT_E = UNIT_M*UNIT_L**2/(UNIT_T**2)
UNIT_E.set_symbole('E')
