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
import cs.parameters
from math import log10, sqrt, log, floor
from cs.units import Unit
from cs.numerical_class import NumericType

SUPPORTED_NUM_TYPES = (int, float)
INT_TYPES = (int)

def sig_exp(num_str):
    parts = num_str.split('.', 2)
    decimal = parts[1] if len(parts) > 1 else ''
    exp = -len(decimal)
    digits = parts[0].lstrip('0') + decimal
    trimmed = digits.rstrip('0')
    exp += len(digits) - len(trimmed)
    sig = int(trimmed) if trimmed else 0
    return sig, exp

def getcs(s):
    '''attention : default removes trailing zeroes !'''
    m, decimalbase = frexp_10(float(s))
    #remove sign
    s = s.lstrip('-')
    #Check for exponential print format
    exp_parts = s.split('e')
    mantissa = exp_parts[0]
#    decimalbase = int(exp_parts[1]) if len(exp_parts)>1 else decimalbase
    #Check for dot (must exist)
    dot_parts = mantissa.split('.')
    left = dot_parts[0].lstrip('0') #remove leading zeroes, for instance 0.1
    digits = dot_parts[1] if len(dot_parts)>1 else ''
    #If not exponential format, first digit is size before dot
    #In case there were only zeroes after the dot or no dot,
    #remove trailing zeroes before the dot
    if len(digits)==0:
        left = left.rstrip('0')
    #In case there were only zeroes before the dot,
    #the leading zeroes after the dot are not relevant
    if len(left)==0:
        digits = digits.lstrip('0')
    cs = len(left)+len(digits)
    lastdigit = decimalbase-cs+1
    return cs, lastdigit

def getbase(val):
    if val == 0:
        return 0
    return floor(log10(abs(val)))

def frexp_10(decimal):
    if decimal == 0:
        return 0, 0
    elif decimal == 1:
        return 1, 0
    if decimal<0:
        sign=-1
        decimal = abs(decimal)
    else:
        sign=1
    logdecimal = log10(decimal)
    base = getbase(decimal)
    return sign * 10**(logdecimal - base), base

def numerical_precision(val):
    ''' retourne la précision numérique du flottant val'''
    assert 0<val<1 and type(val) is float
    J,Q = val.as_integer_ratio()
    while J<2**52: #53 bits
        J *=2
        Q *=2
    return 1/Q
        
class CS():
    def __init__(self, value = None, s = None, cs = None, precision = None, relative_precision = None, cs_precision = 1):
        '''
        sont calculés, selon ce qui est donné en argument
            le nombre de cs
            la précision
            le dernier digit significatif
        le reste (précision relative, premier digit) sont déduits
        
        cs_prec : 1 à 3 CS sur la precision, à choisir, 2 par défaut
        
        recalculer ,revérifier.
        
        calcul auto : basé sur le str de la value
        '''
        #valeur - le calcul auto du CS est basé sur le str
        if value is None:
            self.value = float(s)
        else:
            assert type(value) in SUPPORTED_NUM_TYPES
            self.value = float(value) #ça ne sert à rien d'enregistrer un entier !
            s = str(value) #mais si entier, le calcul auto du CS est important
        
        self.base = getbase(self.value)
        
        #config
        self.cs_precision = cs_precision #nombre de cs sur la prec
        
        #précision
        if cs is not None:
            '''nombre de cs donné'''
            assert type(cs) is int and cs>=0, 'le nombre de CS doit être entier positif'
            self.cs = cs
            self.lastdigit = self.base-cs+1
        elif precision is not None or relative_precision is not None:
            '''précision donnée'''
            m, e = frexp_10(self.value)
            if relative_precision is not None:
                precision = relative_precision*self.value
            precision = abs(precision) #make sure
            mp, ep = frexp_10(precision)
            self.precision = precision
            self.lastdigit = ep
            if e>=ep:
                self.cs = e-ep+1 #à faire mieux ?
            else:
                self.cs = e-ep-1
        else:
            '''détermination automatique'''
            self.cs, self.lastdigit = getcs(s)
        
        if precision is None and relative_precision is None:
            '''mise à jour de la précision'''
            self.precision = 10**(self.lastdigit)
        
        if self.cs>cs.parameters.DIG:
            if cs.parameters.WARNING:
                print("Warning [precision > DIG]: last [{:d}] digit(s) may not be relevant".format(self.cs-cs.parameters.DIG))
        if self.numerical_precision>self.precision:
            self.precision = self.numerical_precision
            if cs.parameters.WARNING:
                print("Warning [precision ({:e}) > numerical precision ({:e})] : precision is bumped to reached numerical precision".format(self.precision, self.numerical_precision))
    
    @property
    def mantisse(self):
        m, e = frexp_10(self.value)
        return m

    @property
    def exposant(self):
        m, e = frexp_10(self.value)
        return e
        
    @property
    def numerical_precision(self):
        return numerical_precision(self.mantisse/10)
    
    @property
    def relative_precision(self):
        return self.precision/self.value

    @property
    def firstdigit(self):
        return self.cs+self.lastdigit-1

    @property
    def confiance(self):
        return cs.parameters.CONFIANCE

    @property
    def sigma(self):
      return self.precision*self.confiance 

    @property
    def valmax(self):
        return self.value+self.sigma

    @property
    def valmin(self):
        return self.value-self.sigma

    def set_csprecision(self, cs):
        self.cs_precision = cs
        
    def set_relatriveprecision(self, r):
        if r is not None:
            self.precision = abs(r*self.value)
    
    def __repr__(self):
        '''à revoir, probleme si ep>e'''
        if -2<=self.base<=0 or self.lastdigit == 0 or (1<=self.base<=3 and self.lastdigit<=0):
            fmt = "{:."+str(abs(self.lastdigit))+"f}" #-self.confiance+1
            p = fmt.format(self.precision)
        else:
            rep = self.cs+self.confiance-2
            if rep>0:
                fmt = "{:."+str(rep)+"e}"
                fmtp = "{:."+str(rep)+"f}e{:+03d}"
            else:
                fmt = "{:"+str(-rep)+".0e}"
                fmtp = "{:."+str(-rep)+"f}e{:+03d}"                
            p = fmtp.format(self.precision*10**(-self.firstdigit), self.firstdigit)
        return fmt.format(self.value)+" ± "+p
    
    def __print__(self):
        return self.__repr__()

    def __str__(self):
        return self.__repr__()

    def _checktype(self, x, operand = '', warning = True, csonly = False, otherwarning = False):
        if (not csonly and not isinstance(x, ALL_SUPPORTED_TYPES)) or (csonly and not isinstance(x, CS)):
            raise TypeError("unsupported operand type(s) for {:s}: 'CS' and '{:s}'".format(operand, type(x).__name__))
        if (warning and isinstance(x, float)) or otherwarning:
            if cs.parameters.WARNING:
                print("Warning [operation not supported]: CS type is lost for operand {:s}".format(operand))
            return False
        return True
            
    def __bool__(self):
        """True if self != 0. Called for bool(self)."""
        return self.value != 0

    def __add__(self, x):
        """self + other"""
        t = self._checktype(x, operand = '+')
        if isinstance(x, int):
            return CS(self.value + x, precision = self.precision)
        elif isinstance(x, float):
            return self.value + CS(x)
        elif t:
            return CS(self.value + x.value, precision = sqrt(self.precision**2+x.precision**2))
        else:
            return self.value+x

    def __radd__(self, other):
        """other + self"""
        return self + other

    def __neg__(self):
        """-self"""
        return CS(-self.value, precision = self.precision)

    def __pos__(self):
        """+self"""
        return self

    def __sub__(self, other):
        """self - other"""
        return self + -other

    def __rsub__(self, other):
        """other - self"""
        return -self + other

    def __mul__(self, x):
        """self * other"""
        t = self._checktype(x, operand = '*')
        if isinstance(x, int):
            return CS(self.value*x, precision = x*self.precision)
        elif isinstance(x, float):
            return self*CS(x)
        elif t:
            return CS(self.value*x.value, relative_precision = sqrt(self.relative_precision**2+x.relative_precision**2))
        else:
            return self.value*x

    def __rmul__(self, other):
        """other * self"""
        raise self * other #commute !

    def __truediv__(self, x):
        """self / other: Should promote to float when necessary."""
        t = self._checktype(x, operand = '/')
        if isinstance(x, int):
            return CS(self.value/x, precision = self.precision/x)
        elif isinstance(x, float):
            return self/CS(x)
        elif t:
            return CS(self.value/x.value, relative_precision = sqrt(self.relative_precision**2+x.relative_precision**2))
        else:
            return self.value/x

    def __rtruediv__(self, x):
        """other / self"""
        t = self._checktype(x, operand = '/')
        if isinstance(x, int):
            return CS(x/self.value, precision = x*self.precision/self.value**2)
        elif isinstance(x, float):
            return CS(x)/self
        elif t:
            return CS(x.value/self.value, relative_precision = sqrt(self.relative_precision**2+x.relative_precision**2))
        else:
            return x/self.value

    def __pow__(self, x):
        """self**exponent; should promote to float or complex when necessary."""
        t = self._checktype(x, operand = '**')
        if isinstance(x, int):
            return CS(self.value**x, precision = x*self.precision*self.value**(x-1))
        elif isinstance(x, float):
            return self**CS(x)
        elif t:
            return CS(self.value**x.value, relative_precision = sqrt((x.value/self.value*self.relative_precision)**2+(log(self.value)*x.relative_precision)**2))
        else:
            return self.value**x

    def __rpow__(self, x):
        """base ** self"""
        t = self._checktype(x, operand = '**')
        if isinstance(x, int):
            return CS(x**self.value, precision = log(x)*self.precision*self.value)
        elif isinstance(x, float):
            return CS(x)**self
        elif t:
            return CS(x.value**self.value, relative_precision = sqrt((self.value/x.value*x.relative_precision)**2+(log(x.value)*self.relative_precision)**2))
        else:
            return self.value**x

    def __abs__(self):
        """Returns the Real distance from 0. Called for abs(self)."""
        return CS(abs(self.value), precision = self.precision)

    def __eq__(self, other):
        """self == other"""
        global SUPPORTED_NUM_TYPES
        if isinstance(other, SUPPORTED_NUM_TYPES):
            return self.valmin <= other <= self.valmax
        elif isinstance(other, CS):
            return self.valmin<=other.value<=self.valmax or other.valmin<=self.value<=other.valmax
        else:
            raise NotImplementedError

    def __float__(self):
        """Any Real can be converted to a native float object.
        Called for float(self)."""
        return float(self.value)

    def __trunc__(self):
        """trunc(self): Truncates self to an Integral.
        Returns an Integral i such that:
          * i>0 iff self>0;
          * abs(i) <= abs(self);
          * for any Integral j satisfying the first two conditions,
            abs(i) >= abs(j) [i.e. i has "maximal" abs among those].
        i.e. "truncate towards 0".
        """
        if self.value-self.sigma>0:
            return self.__floor__()
        elif self.value+self.sigma<0:
            return self.__ceil__()
        #sinon on est autour de zéro, on se base sur la valeur centrale
        elif self.value>0:
            self.__floor__()
        elif self.value<0:
            self.__ceil__()
        else:
            #zéro
            return 0

    def __floor__(self):
        """Finds the greatest Integral <= self."""
        return self//1

    def __ceil__(self):
        """Finds the least Integral >= self."""
        return self//1+1

    def __round__(self, ndigits=None):
        """Rounds self to ndigits decimal places, defaulting to 0.
        If ndigits is omitted or None, returns an Integral, otherwise
        returns a Real. Rounds half toward even.
        """
        if ndigits is None:
            ncs = 0
        else:
            ncs = ndigits
        return CS(round(self.value, ndigits), cs = ncs)

    def __divmod__(self, other):
        """divmod(self, other): The pair (self // other, self % other).
        Sometimes this can be computed faster than the pair of
        operations.
        """
        self._checktype(other, operand = '%')
        div = self // other
        return (div, self - div*other)

    def __rdivmod__(self, other):
        """divmod(other, self): The pair (self // other, self % other).
        Sometimes this can be computed faster than the pair of
        operations.
        """
        return (other // self, other % self)

    def __floordiv__(self, other):
        """self // other: The int() of self/other."""
        self._checktype(other, operand = '//')
        global SUPPORTED_NUM_TYPES
        if isinstance(other, SUPPORTED_NUM_TYPES):
            maxdiv = int(self.valmax//other)
            mindiv = int(self.valmin//other)
        else:
            maxdiv = int(self.valmax//other.valmin)
            mindiv = int(self.valmin//other.valmax)
        print(maxdiv, mindiv)
        precision = (maxdiv-mindiv)/2
        if precision == 0:
            return maxdiv
        else:
            return CS(int((maxdiv+mindiv)/2), precision = precision)

    def __rfloordiv__(self, other):
        """other // self: The int() of other/self."""
        self._checktype(other, operand = '//')
        maxdiv = int(other//self.valmin)
        mindiv = int(other//self.valmax)
        precision = (maxdiv-mindiv)/2
        if precision == 0:
            return maxdiv
        else:
            return CS(int((maxdiv+mindiv)/2), precision = precision)

    def __mod__(self, other):
        """self % other"""
        return self.__divmod__(other)[1]

    def __rmod__(self, other):
        """other % self"""
        div = self.__rfloordiv__(other)
        return other-self*div

    def __lt__(self, other):
        """self < other
        < on Reals defines a total ordering, except perhaps for NaN."""
        global SUPPORTED_NUM_TYPES
        if isinstance(other, SUPPORTED_NUM_TYPES):
            return self.valmin < other 
        elif isinstance(other, CS):
            return self.valmin < other.valmax
        else:
            raise NotImplementedError

    def __le__(self, other):
        """self <= other"""
        global SUPPORTED_NUM_TYPES
        if isinstance(other, SUPPORTED_NUM_TYPES):
            return self.valmin <= other 
        elif isinstance(other, CS):
            return self.valmin <= other.valmax
        else:
            raise NotImplementedError

    def __gt__(self, other):
        """self > other
        < on Reals defines a total ordering, except perhaps for NaN."""
        global SUPPORTED_NUM_TYPES
        if isinstance(other, SUPPORTED_NUM_TYPES):
            return self.valmax > other 
        elif isinstance(other, CS):
            return self.valmax > other.valmin
        else:
            raise NotImplementedError

    def __ge__(self, other):
        """self >= other"""
        global SUPPORTED_NUM_TYPES
        if isinstance(other, SUPPORTED_NUM_TYPES):
            return self.valmax >= other 
        elif isinstance(other, CS):
            return self.valmax >= other.valmin
        else:
            raise NotImplementedError

    def __complex__(self):
        """complex(self) == complex(float(self), 0)"""
        return complex(float(self))

    def __iadd__(self, x):
        t = self._checktype(x, operand = '+=')
        if isinstance(x, int):
            self.value += x
        elif t:
            self.value += x.value
            self.precision = sqrt(self.precision**2+x.precision**2)
        else:
            self.value += CS(x)
        return self

    def __isub__(self, x):
        self._checktype(x, operand = '-=')
        self += -x
        return self

    def __imul__(self, x):
        t = self._checktype(x, operand = '*=')
        if isinstance(x, int):
            self.value *= x
            self.precision *= x
        elif t:
            self.value *= x.value
            self.set_relative_precision(sqrt(self.relative_precision**2+x.relative_precision**2))
        else:
            y = CS(x)
            self.value *= y.value
            self.set_relative_precision(sqrt(self.relative_precision**2+y.relative_precision**2))
        return self

    def __itruediv__(self, x):
        self._checktype(x, operand = '/=')
        self *= 1/x
        return self

ALL_SUPPORTED_TYPES = (*SUPPORTED_NUM_TYPES, CS)

class CSalt(NumericType):
    def __init__(self, value = None, s = None, cs = None, precision = None, relative_precision = None, cs_precision = 1):
        '''
        sont calculés, selon ce qui est donné en argument
            le nombre de cs
            la précision
            le dernier digit significatif
        le reste (précision relative, premier digit) sont déduits
        
        cs_prec : 1 à 3 CS sur la precision, à choisir, 2 par défaut
        
        recalculer ,revérifier.
        
        calcul auto : basé sur le str de la value
        '''

        NumericType.__init__(value, return_class = CSalt, properties = ['precision'])
    
        #valeur - le calcul auto du CS est basé sur le str
        if value is None:
            self.value = float(s)
        else:
            assert type(value) in SUPPORTED_NUM_TYPES
            self.value = float(value) #ça ne sert à rien d'enregistrer un entier !
            s = str(value) #mais si entier, le calcul auto du CS est important
        
        self.base = getbase(self.value)
        
        #config
        self.cs_precision = cs_precision #nombre de cs sur la prec
        
        #précision
        if cs is not None:
            '''nombre de cs donné'''
            assert type(cs) is int and cs>=0, 'le nombre de CS doit être entier positif'
            self.cs = cs
            self.lastdigit = self.base-cs+1
        elif precision is not None or relative_precision is not None:
            '''précision donnée'''
            m, e = frexp_10(self.value)
            if relative_precision is not None:
                precision = relative_precision*self.value
            precision = abs(precision) #make sure
            mp, ep = frexp_10(precision)
            self.precision = precision
            self.lastdigit = ep
            if e>=ep:
                self.cs = e-ep+1 #à faire mieux ?
            else:
                self.cs = e-ep-1
        else:
            '''détermination automatique'''
            self.cs, self.lastdigit = getcs(s)
        
        if precision is None and relative_precision is None:
            '''mise à jour de la précision'''
            self.precision = 10**(self.lastdigit)
        
        if self.cs>cs.parameters.DIG:
            if cs.parameters.WARNING:
                print("Warning [precision > DIG]: last [{:d}] digit(s) may not be relevant".format(self.cs-cs.parameters.DIG))
        if self.numerical_precision>self.precision:
            self.precision = self.numerical_precision
            if cs.parameters.WARNING:
                print("Warning [precision ({:e}) > numerical precision ({:e})] : precision is bumped to reached numerical precision".format(self.precision, self.numerical_precision))
    
    def _set_operations(self):
        def mul_prop_func(x,y):
            return {'relative_precision':sqrt(x.relative_precision**2+y.relative_precision**2)}
        self.operations['*'].set_prop_func(mul_prop_func)
        
        def add_prop_func(x,y):
            return {'precision':sqrt(x.precision**2+y.precision**2)}
        self.operations['+'].set_prop_func(add_prop_func)
        
    @property
    def mantisse(self):
        m, e = frexp_10(self.value)
        return m

    @property
    def exposant(self):
        m, e = frexp_10(self.value)
        return e
        
    @property
    def numerical_precision(self):
        return numerical_precision(self.mantisse/10)
    
    @property
    def relative_precision(self):
        return self.precision/self.value

    @property
    def firstdigit(self):
        return self.cs+self.lastdigit-1

    @property
    def confiance(self):
        return cs.parameters.CONFIANCE

    @property
    def sigma(self):
      return self.precision*self.confiance 

    @property
    def valmax(self):
        return self.value+self.sigma

    @property
    def valmin(self):
        return self.value-self.sigma

    def set_csprecision(self, cs):
        self.cs_precision = cs
        
    def set_relatriveprecision(self, r):
        if r is not None:
            self.precision = abs(r*self.value)
    
    def __repr__(self):
        '''à revoir, probleme si ep>e'''
        if -2<=self.base<=0 or self.lastdigit == 0 or (1<=self.base<=3 and self.lastdigit<=0):
            fmt = "{:."+str(abs(self.lastdigit))+"f}" #-self.confiance+1
            p = fmt.format(self.precision)
        else:
            rep = self.cs+self.confiance-2
            if rep>0:
                fmt = "{:."+str(rep)+"e}"
                fmtp = "{:."+str(rep)+"f}e{:+03d}"
            else:
                fmt = "{:"+str(-rep)+".0e}"
                fmtp = "{:."+str(-rep)+"f}e{:+03d}"                
            p = fmtp.format(self.precision*10**(-self.firstdigit), self.firstdigit)
        return fmt.format(self.value)+" ± "+p
    