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
import sys
DIG = sys.float_info.dig #The sys.float_info.dig tells how many decimal digits are guaranteed to be always precisely printed in str

WARNING = True
CONFIANCE = 2

def set_warnings(warning = True):
    global WARNING
    assert warning or not warning #erreur si cela ne s'évalue pas en bool...
    WARNING = warning

def set_confiance(c = 1):
    global CONFIANCE
    assert type(c) is int and c>=1
    CONFIANCE = c

