#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 16:53:03 2017

@author: elessar

Units class

TODO :
    Implement UNITS and factors conversions
        units with symbolic package

"""
from cs.grandeurs import SI

def Constante(val, unit):
    return SI(value = val, unit = unit, precision = 0, warning = False)

        
CTES = {'c': Constante(299792458,'m.s^-1'),
        'e': Constante(1.602176634e-19, 'C'),
        'h': Constante(6.62607015e-34, 'J.s'),
        'k': Constante(1.380649e-23, 'J.K^-1'),
        'NA': Constante(6.02214076e23,'mol^-1')} #en SI, valeurs 2017
