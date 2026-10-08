#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 16:53:03 2017

@author: elessar

Numeric class

TODO :
    base on DECIMAL class
    
    REPR
    
    Implement all statistical methods (choix de la distribution, de l'intervalle de confiance, student...)
    
    Calcul type A : CS(typeA = [1, 2, 3, ...])

    Implement UNITS and factors conversions
        units with symbolic package

    checktypes évolé pour faire des sous classes aisément
    
    faire évoluer toutes les fonctions de math et numpy (@)

    prendre en compte les facteurs de conversion (sans CS, constantes physiques, unités...)
    
3 cas :
    - d << v
    - d approx v
    - d >> v
    
"""
from cs.CS import CS
from cs.parameters import set_confiance, set_warnings
from cs.units import Unit
from cs.constantes import Constante, CTES
from cs.grandeurs import SI
