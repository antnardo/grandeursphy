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
import cs.parameters as PARAMETERS
from math import log10, sqrt, log, floor
from cs.numerical_class import NumericType

#def sig_exp(num_str):
#    parts = num_str.split('.', 2)
#    decimal = parts[1] if len(parts) > 1 else ''
#    exp = -len(decimal)
#    digits = parts[0].lstrip('0') + decimal
#    trimmed = digits.rstrip('0')
#    exp += len(digits) - len(trimmed)
#    sig = int(trimmed) if trimmed else 0
#    return sig, exp

def getcs(s):
    '''attention : default removes trailing zeroes !'''
#    m, decimalbase = frexp_10(float(s))
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
    return cs

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
    assert type(val) is float
    e = int(val.hex().split('p')[1]) #exposant en base 2
    #en 64 bits : 14 chiffres hexadecimaux, 4*N-4 = 52
    d = e-52
    return float.fromhex('0x1p{:d}'.format(d)) #=1*2**(e-4*N+4)=1/16**(N-1)*2**e

def numerical_precision_old(val):
    ''' retourne la précision numérique du flottant val'''
    assert 0<val<1 and type(val) is float
    J,Q = val.as_integer_ratio()
    while J<2**52: #53 bits
        J *=2
        Q *=2
    return 1/Q

class CS(NumericType):
    def __init__(self, value, cs = None, precision = None, relative_precision = None, cs_precision = 1, warning = None, **kwargs):
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
        #Définition de toutes les opérations de base sur self.value
        NumericType.__init__(self, value, typename = "CS", **kwargs)
    
        #valeur - le calcul auto du CS est basé sur le type
        if type(value) is str:
            self.value = float(value)
            s = value
        elif type(value) is CS:
            self.value = value.value
            if precision is None:
                precision = value.precision
            if cs_precision is None:
                cs_precision = value.precision
            if warning is None:
                warning  = value.warning
        else:
            assert type(value) in self.SUPPORTED_NUM_TYPES
            self.value = float(value) #ça ne sert à rien d'enregistrer un entier !
            s = str(value) #mais si entier, le calcul auto du CS est important
        
        #config
        self.cs_precision = cs_precision #nombre de cs sur la precision
        if warning is None:
            self.warning = PARAMETERS.WARNING
        else:
            self.warning = warning
        
        #précision
        if cs is not None:
            '''nombre de cs donné'''
            self.set_cs(cs)
        elif precision is not None:
            '''précision donnée'''
            self.set_precision(precision)
        elif relative_precision is not None:
            self.set_relativeprecision(relative_precision)
        else:
            '''détermination automatique'''
            self.set_cs(getcs(s))
        
        #warnings
        if self.cs>PARAMETERS.DIG:
            if self.warning:
                print("{:} : Warning [precision > DIG]: last [{:d}] digit(s) may not be relevant".format(self, self.cs-PARAMETERS.DIG))

    #set properties
    def set_precision(self, p):
        if p<0:
            p = -p
        if self.numerical_precision>p:
            if self.warning:
                print(self)
                print("{:} : Warning [precision ({:e}) > numerical precision ({:e})] : precision is bumped to reached numerical precision".format(self, self.precision, self.numerical_precision))
            self.precision = self.numerical_precision
        else:
            self.precision = p
        
    def set_relativeprecision(self, r):
        self.set_precision(r*self.value)
    
    def set_cs(self, cs):
        assert type(cs) is int and cs>=0, 'le nombre de CS doit être entier positif'
        self.set_precision(10**(self.firstdigit-cs+1))

    #options
    def set_csprecision(self, cs):
        self.cs_precision = cs
    
    #properties
    @property
    def firstdigit(self):
        return getbase(self.value)
    
    @property
    def lastdigit(self):
        return getbase(self.precision)

    @property
    def cs(self):
        ''' A REVOIR '''
        return self.firstdigit - self.lastdigit
        
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
        return numerical_precision(self.mantisse/10)*10**(self.exposant+1)
    
    @property
    def relative_precision(self):
        return self.precision/self.value

    @property
    def confiance(self):
        return PARAMETERS.CONFIANCE

    @property
    def sigma(self):
      return self.precision*self.confiance 

    @property
    def valmax(self):
        return self.value+self.sigma

    @property
    def valmin(self):
        return self.value-self.sigma

    def __repr__(self):
        '''à revoir, probleme si ep>e'''
        if -2<=self.firstdigit<=0 or self.lastdigit == 0 or (1<=self.firstdigit<=3 and self.lastdigit<=0):
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

    def _setoperators(self):
        super()._setoperators()
        #MULTIPLICATION
        def mul_prop_func(x,y):
            return {'relative_precision':sqrt(x.relative_precision**2+y.relative_precision**2)}
        def mul_const_func(x,y):
            return {'precision':x.precision*y}
        self.operators['*'].set_prop_func(mul_prop_func)
        self.operators['*'].set_const_func(mul_const_func)
        
        #DIVISION
        def div_prop_func(x,y):
            return {'relative_precision': sqrt((y.value/x.value*x.relative_precision)**2+(log(x.value)*y.relative_precision)**2)}
        def div_const_func(x,y):
            return {'precision': x.precision/y}
        def div_inv_const_func(x,y):
            return {'precision': y*x.precision/x.value**2}
        self.operators['/'].set_prop_func(div_prop_func)
        self.operators['/'].set_const_func(div_const_func)
        self.operators['/'].set_inv_const_func(div_inv_const_func)

        #ADDITION
        def add_prop_func(x,y):
            return {'precision':sqrt(x.precision**2+y.precision**2)}
        self.operators['+'].set_prop_func(add_prop_func)

        #PUISSANCE
        def pow_prop_func(x,y):
            return {'relative_precision': sqrt(x.relative_precision**2+y.relative_precision**2)}
        def pow_const_func(x,y):
            return {'precision': y*x.precision*x.value**(y-1)}
        def pow_inv_const_func(x,y):
            return {'precision':log(y)*x.precision*x.value}
        self.operators['**'].set_prop_func(pow_prop_func)
        self.operators['**'].set_const_func(pow_const_func)
        self.operators['**'].set_inv_const_func(pow_inv_const_func)
        
    #COMPORTEMENTS SPECIFIQUES
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

    def __floordiv__(self, other):
        """self // other: The int() of self/other."""
        t = self._checktype(other, operand = '//')
        if t:
            maxdiv = int(self.valmax//other.valmin)
            mindiv = int(self.valmin//other.valmax)
        else:
            maxdiv = int(self.valmax//other)
            mindiv = int(self.valmin//other)
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

    def __eq__(self, other):
        """self == other"""
        t = self._checktype(other, operand = '=')
        if isinstance(other, self.SUPPORTED_NUM_TYPES):
            return self.valmin <= other <= self.valmax
        elif t:
            return self.valmin<=other.value<=self.valmax or other.valmin<=self.value<=other.valmax
        else:
            raise NotImplementedError

    def __lt__(self, other):
        """self < other
        < on Reals defines a total ordering, except perhaps for NaN."""
        t = self._checktype(other, operand = '<')
        if isinstance(other, self.SUPPORTED_NUM_TYPES):
            return self.valmin < other 
        elif t:
            return self.valmin < other.valmax
        else:
            raise NotImplementedError

'''
#TESTS
assert cs.getbase(5) == 0
assert cs.getbase(50) == 1
assert cs.getbase(500) == 2
assert cs.getbase(0.5) == -1
assert cs.getbase(1) == 0
assert cs.getbase(10) == 1
assert cs.getbase(100) == 2
assert cs.getbase(0.1) == -1

asserttuple(cs.frexp_10(5),(5,0))
asserttuple(cs.frexp_10(50), (5,1))
asserttuple(cs.frexp_10(500), (5,2))
asserttuple(cs.frexp_10(0.5), (5,-1))
asserttuple(cs.frexp_10(1), (1,0))
asserttuple(cs.frexp_10(10), (1,1))
asserttuple(cs.frexp_10(100), (1,2))
asserttuple(cs.frexp_10(0.1), (1,-1))

asserttuple(cs.getcs('1000.000'), (7, -3))
asserttuple(cs.getcs('1'), (1, 0))
asserttuple(cs.getcs('1.0e3'), (2, 2))
asserttuple(cs.getcs(str(1.0e3)), (5, -1))

'''
