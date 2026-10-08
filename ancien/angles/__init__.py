#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 16:53:03 2017

@author: elessar

Angle numeric class
To ease deg and radian conversion

TODO :
    CS sur les rad, influence sur les deg, min, sec

"""
from math import pi
from cs import CS

SUPPORTED_NUM_TYPES = (int, float)

DEG_CONVERSION = 180/pi
MIN_CONVERSION = DEG_CONVERSION*60
SEC_CONVERSION = MIN_CONVERSION*60
    
class Angle():
    def __init__(self, rad = None, deg = None, min = None, sec = None, precision=2, minunit = "'", secunit = '"', repr_is_deg = True, modulo=True):
        assert not(rad is None and deg is None and min is None and sec is None), 'valeur initiale à donner en rad ou deg'
        global DEG_CONVERSION, MIN_CONVERSION, SEC_CONVERSION
        minprecision = None
        if deg is not None or min is not None or sec is not None:
            if sec is None:
                sec = 0
            else:
                minprecision = 'sec'
            if min is None:
                min = 0
            elif minprecision is None:
                minprecision = 'min'
            if deg is None:
                deg = 0
            elif minprecision is None:
                minprecision = 'deg'
            rad = deg/DEG_CONVERSION+min/MIN_CONVERSION+sec/SEC_CONVERSION
        self.modulo = modulo
        self.setrad(rad)
        self.precision = precision
        self.minunit = minunit
        self.secunit = secunit
        self.degunit = '°'
        self.repr_is_deg = repr_is_deg
    
    @property #call : Angle.deg instead of Angle.deg()
    def deg(self):
        global DEG_CONVERSION
        return self.rad*DEG_CONVERSION

    @property
    def min(self):
        global MIN_CONVERSION
        return self.rad*MIN_CONVERSION

    @property
    def sec(self):
        global SEC_CONVERSION
        return self.rad*SEC_CONVERSION
    
    def setrad(self, rad):
        if self.modulo:
            self.rad = rad%(2*pi)
        else:
            self.rad = rad

    @property
    def degmin(self):
        d = self.deg
        degres = int(d)
        m = (d-degres)*60
        return degres, m

    @property
    def minsec(self):
        m = self.min
        min = int(m)
        s = (m-min)*60
        return min, s
    
    @property
    def degminsec(self):
        deg, m = self.degmin
        min = int(m)
        s = (m-min)*60
        return deg, min, s
    
    def _formatvalue(self, x, unit, zeros = 0, precision = None):
        if type(x) is int:
            if zeros>0:
                fmt = "{:0"+str(zeros)+"d}"
                return fmt.format(x)+unit
            else:
                return "{:d}".format(x)+unit
        else:
            if precision is None:
                fmt = "{:."+str(self.precision)+"f}"
            else:
                fmt = "{:."+str(precision)+"f}"
            return fmt.format(x)+unit
    
    def format(self, fmt, **kwargs):
        if fmt == 'd':
            return self._formatvalue(self.deg, self.degunit, **kwargs)
        elif fmt == 'm':
            return self._formatvalue(self.min, self.minunit, **kwargs)
        elif fmt == 's':
            return self._formatvalue(self.sec, self.secunit, **kwargs)
        elif fmt == 'dm':
            d,m = self.degmin
            fdeg = self._formatvalue(d, self.degunit, **kwargs)
            fmin = self._formatvalue(m, self.minunit, **kwargs)
            return fdeg+fmin
        elif fmt == 'dms':
            d,m,s = self.degminsec
            fdeg = self._formatvalue(d, self.degunit, **kwargs)
            fmin = self._formatvalue(m, self.minunit, zeros = 2, **kwargs)
            fsec = self._formatvalue(s, self.secunit, zeros = 2, **kwargs)
            return fdeg+fmin+fsec
        elif fmt == 'ms':
            m,s = self.minsec
            fmin = self._formatvalue(m, self.minunit, **kwargs)
            fsec = self._formatvalue(s, self.secunit, zeros = 2, **kwargs)
            return fmin+fsec
        elif fmt == 'rad':
            return "{:}".format(self.rad)
    
    def __repr__(self):
        return f'Angle(rad={self.rad}, precision={self.precision}, modulo={self.modulo})'

    def __print__(self):
        if self.repr_is_deg:
            return self.format('dms')
        else:
            return self.format('rad')
    
    def _checktype(self, x, operand = '', angle=False):
        global SUPPORTED_NUM_TYPES
        if angle:
            types = (*SUPPORTED_NUM_TYPES, Angle)
        else:
            types = SUPPORTED_NUM_TYPES
        if not isinstance(x, types):
            raise TypeError("unsupported operand type(s) for {:s}: 'Angle' and '{:s}'".format(operand, type(x).__name__))
        if angle and type(x) is Angle:
                return x.rad
        return x
            
    def __add__(self, x):
        y = self._checktype(x, operand = '+', angle = True)
        return Angle(rad = self.rad+y)

    def __sub__(self, x):
        return self.__add__(-x)

    def __mul__(self, x):
        y = self._checktype(x, operand = '*', angle=True)
        if type(x) is Angle:
            return self.rad*y
        return Angle(rad = self.rad*y)

    def __truediv__(self, x):
        y = self._checktype(x, operand = '/', angle = True)
        if type(x) is Angle:
            return self.rad/y
        return Angle(rad = self.rad/y)
        
    def __floordiv__(self, x):
        y = self._checktype(x, operand = '//', angle = True)
        if type(x) is Angle:
            return self.rad//y
        return Angle(rad = self.rad//y)
        
    def __mod__(self, x):
        y = self._checktype(x, operand = '@', angle = True)
        if type(x) is Angle:
            return self.rad%y
        return Angle(self.rad%y)

    def __pow__(self, x, operand = '**'):
        self._checktype(x)
        return self.rad**x

    def __radd__(self, x):
        return self + x
    
    def __rsub__(self, x):
        return -self + x
    
    def __rmul__(self, x):
        return self * x
    
    def __iadd__(self, x):
        y = self._checktype(x, operand = '+=', angle = True)
        self.setrad(self.rad+ y)
        return self

    def __isub__(self, x):
        y = self._checktype(x, operand = '-=', angle = True)
        self.setrad(self.rad-y)
        return self

    def __imul__(self, x):
        self._checktype(x, operand = '*=')
        self.setrad(self.rad*x)
        return self

    def __itruediv__(self, x):
        self._checktype(x, operand = '/=')
        self.setrad(self.rad/x)
        return self

    def __ifloordiv__(self, x):
        self._checktype(x, operand = '//=')
        self.setrad(self.rad//x)
        return self

    def __imod__(self, x):
        self._checktype(x, operand = '@=')
        self.setrad(self.rad%x)
        return self

    def __neg__(self):
        return Angle(rad=-self.rad)

    def __pos__(self):
        return Angle(rad=self.rad)

    def __abs__(self):
        return Angle(rad=abs(self.rad))

    def __round__(self, n=None):
        return Angle(rad=round(self.rad, n))