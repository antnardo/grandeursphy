from decimal import ExtendedContext, setcontext

setcontext(ExtendedContext)

from .SI import *
from .units import *
from .interactions import *
from .particules import *
from .astro import *
from .US import *
from .CGS import *

# __CONSTANTES__ = [] + __CONSTANTES_US__