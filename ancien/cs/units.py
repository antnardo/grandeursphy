#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 16:53:03 2017

@author: elessar

Units class

TODO :
    Implement UNITS and factors conversions
        units with symbolic package
    
    Fractions dans les puissances

"""
from cs.CS import CS

SI = ['m', 'kg', 's', 'K', 'cd', 'mol', 'C']

MUL = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
DIV = ['m', 'µ', 'n', 'p', 'f', 'a', 'z', 'y']

MULS = {'k': 3, 'M': 6, 'G': 9, 'T': 12, 'P': 15, 'E': 18, 'Z': 21, 'Y': 24,
        'm':-3, 'µ':-6, 'n':-9, 'p':-12, 'f':-15, 'a':-18, 'z':-21, 'y':-24,
        '':0, 'd':-1, 'c':-2, 'h':2}

NONSI = {'N':'kg.m.s^-2',
         'J':'kg.m^2.s^-2',
         'Pa':'kg.m^-1.s^-2',
         'T':'kkg',
         'g':'mkg'}

CONST = ['rad', '°']

#DICTIONNAIRES
def emptySI():
    d = {}
    for unit in SI:
        d[unit] = 0
    return d

def mulSI(d1, d2):
    d = emptySI()
    for k in d:
        d[k] = d1[k]+d2[k]
    return d

def negSI(d1):
    d = emptySI()
    for k in d:
        d[k] = -d1[k]
    return d

def equalSI(d1, d2):
    for k,v in d1.items():
        if not d2[k] == v:
            return False
    return True

#COEF MULTIPLICATEURS
INVMULS = {v:k for k,v in MULS.items()}
MULvals = sorted(list(MULS.values()))

def lastvalue(L, value):
    '''L should be sorted, value superior to L[0]
    get last element inferior to value'''
    x = L[0]
    assert value>=x
    i = 1
    while i<len(L):
        if L[i]>value:
            return x
        x = L[i]
        i += 1
    return x

def coef_multiplicateur(s):
    return MULS[s]
    
def multiplieur(u):
    if u in SI:
        return 0,u
    if u[0] in MULS:
        return MULS[u[0]], u[1:]
    return 0, u

def multiplieur_to_string(m):
    mulval = lastvalue(MULvals, m)
    mul = INVMULS[mulval]
    return mul, m-mulval

#DECOMPOSITION
def decompose(s):
    '''renvoit un faceutr numérique, une puissance de 10 et un dictionnaire d'unités SI contenant les puissances'''
    liste = s.split('.')
    mul = 0
    L = emptySI()
    coef = 1
    for unit in liste:
        m,u,p = puissance(unit)
        mul += m
        if u in SI:
            L[u] += p
        elif u in NONSI:
            nonsi_c, nonsi_mul, nonsi_L = decompose(NONSI[u])
            for un, pn in nonsi_L.items():
                L[un] += pn*p
            mul += nonsi_mul
            coef *= nonsi_c
        elif u in UNIT_CONV:
            fact_unit = UNIT_CONV[u]
            for uf,pf in fact_unit.units.items():
                L[uf] += pf*p
            coef*=fact_unit.coef
            mul+=fact_unit.mul
        else:
            raise ValueError('unité non reconnue')
    return coef, mul, L  
    
def puissance(s):
    liste = s.split('^')
    u = liste[0]
    p = liste[1] if len(liste)>1 else 1
    try:
        power = int(p)
    except ValueError:
        try: #puissance fractionnelle ?
            power = eval(p)
        except ValueError: 
            pass
    m, u = multiplieur(u)
    return m,u,power

#RECOMPOSITION
def unit_string(dic) :
    s = ''
    for k,v in dic.items():
        if v!=0:
            if s!='':
                s += '·'
            s += k
            if v!=1:
                if type(v) is int:
                    s += '^({:d})'.format(v)
                else:
                    s += '^({:.2f})'.format(v)
    return s

#------- CLASS --------
class Unit(object):
    def __init__(self, s = '', m = None, u = None, coef = 1):
        if m is not None and u is not None:
            c, self.mul, self.units = 1, m, u
        else:
            c, self.mul, self.units = decompose(s)
        self.shifted = 0
        self.coef = CS(value = c*coef, precision = 0, warning = False)
    
    def shift_mul(self, m):
        self.mul += m
        self.shifted += m
    
    def release_mul(self):
        self.mul -= self.shifted
        self.shifted = 0
        
    def __repr__(self):
        smul, r = multiplieur_to_string(self.mul)
        s = ''
        if self.coef !=1:
            s += 'x '+repr(self.coef)+' '
        if r !=0:
            s += 'x 10^{:d} '.format(r)
        s += smul
        s += unit_string(self.units)
        return s
    
    def __str__(self):
        return self.__repr__()
    
    def __mul__(self, other):
        if isinstance(other, Unit):
            m = self.mul+other.mul
            u = mulSI(self.units, other.units)
            return Unit(m = m, u = u)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self*other

    def __neg__(self, other):
        if isinstance(other, Unit):
            return Unit(m = self.m, u = negSI(self.units))
        else:
            return NotImplemented
        
    def __truediv__(self, other):
        return self*(-other)

    def __rtruediv__(self, other):
        return (-self)*other

    def __eq__(self, other):
        if isinstance(other, Unit):
            return self.m == other.m and equalSI(self.units, other.units)
        else:
            return NotImplemented

def Facteur(val, unit = ''):
    return Unit(unit, coef = val)

UNIT_CONV = {'in' : Facteur(2.54, 'cm')}


