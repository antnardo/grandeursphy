#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 16:53:03 2017

@author: elessar

Numeric class

TODO :
    base on DECIMAL class
    
    toujours mettre le multiplicateur de l'unité dans la valeur

    prendre en compte les facteurs de conversion (sans CS, constantes physiques, unités...)
    
    
"""
from cs.CS import CS
from cs.units import Unit, coef_multiplicateur

class SI(CS):
    def __init__(self, value, unit = '', cs = None, precision = None, relative_precision = None, cs_precision = 1, warning = True):
        CS.__init__(self, value, cs, precision, relative_precision, cs_precision, warning, add_supported_types = CS, add_converted_types = CS)
        self.unit = Unit(unit)
        m = 10**self.unit.mul
        self.value *= m
        self.precision *= m
        
        #pour l'affichage, transfert du multiplicateur, l'unité est donc en SI
        self.coef_multiplicateur = self.unit.mul
        self.unit.mul = 0
        
    def set_multiplicateur(self, M):
        if M == '':
            self.coef_multiplicateur = 0
        elif type(M) is str:
            self.coef_multiplicateur = coef_multiplicateur(M)
        elif type(M) is int:
            self.coef_multiplicateur = M
        else:
            raise NotImplementedError
            
    def __repr__(self):
        self.unit.shift_mul(self.coef_multiplicateur)
        if self.coef_multiplicateur==0:
            valeur = CS(self.value, precision = self.precision)
        elif self.coef_multiplicateur>0:
            valeur = CS(self.value, precision = self.precision)/10**self.coef_multiplicateur
        else:
            valeur = CS(self.value, precision = self.precision)*10**self.coef_multiplicateur
        s = repr(valeur) +' '+ repr(self.unit)
        self.unit.release_mul()
        return s
    
    def __str__(self):
        return self.__repr__()
    
    def _compatibility(self, x, operand, othertype, **kwargs):
        test = super()._compatibility(x, operand, othertype, **kwargs)
        if operand in ['+', '=', '<']:
            if isinstance(x, self.SUPPORTED_NUM_TYPES):
                unit = Unit('')
            else:
                unit = x.unit
            return test and self.unit == unit
        else:
            return test

    def _setoperators(self):
        super()._setoperators()
        #MULTIPLICATION
        def mul_prop_func(x,y):
            return {'unit':x.unit*y.unit}
        def mul_const_func(x,y):
            return {'unit':x.unit}
        self.operators['*'].add_prop_func(mul_prop_func)
        self.operators['*'].add_const_func(mul_const_func)
        
        #ADDITION
        def add_prop_func(x,y):
            return {'unit':x.unit}
        self.operators['+'].set_prop_func(add_prop_func)

        #DIVISION
        def div_prop_func(x,y):
            return {'unit': x.unit/y.unit}
        def div_const_func(x,y):
            return {'unit': x.unit}
        def div_inv_const_func(x,y):
            return {'unit': x.unit}
        self.operators['/'].add_prop_func(div_prop_func)
        self.operators['/'].add_const_func(div_const_func)
        self.operators['/'].add_inv_const_func(div_inv_const_func)

