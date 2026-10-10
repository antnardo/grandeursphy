"""Unités anglo-saxonnes, en grandeurs SI (accord de 1959 sur le yard et la livre)."""

from grandeurs.constantes._fiches import US, exacte

__all__ = [
    "FL_OZ",
    "FL_OZ_IMP",
    "FOOT",
    "GAL_IMP",
    "GAL_US",
    "INCH",
    "LB_AV",
    "MILE",
    "OZ_AV",
    "YARD",
]

INCH = exacte("INCH", 0.0254, "m", "pouce", US)
FOOT = exacte("FOOT", 0.3048, "m", "pied, 12 pouces", US)
YARD = exacte("YARD", 0.9144, "m", "yard, 3 pieds", US)
MILE = exacte("MILE", 1609.344, "m", "mile terrestre, 1760 yards", US)
GAL_US = exacte("GAL_US", 3.785411784e-3, "m^3", "gallon américain, 231 pouces cubes", US)
FL_OZ = exacte("FL_OZ", 3.785411784e-3 / 128, "m^3", "once liquide américaine", US)
GAL_IMP = exacte("GAL_IMP", 4.54609e-3, "m^3", "gallon impérial (britannique)", US)
FL_OZ_IMP = exacte("FL_OZ_IMP", 4.54609e-3 / 160, "m^3", "once liquide impériale", US)
LB_AV = exacte("LB_AV", 0.45359237, "kg", "livre avoirdupois", US)
OZ_AV = exacte("OZ_AV", 0.45359237 / 16, "kg", "once avoirdupois", US)
