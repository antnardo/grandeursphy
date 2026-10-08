#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:34:29 2017

@author: elessar

TODO : avoir des propriétés, et des règles d'addition/multiplication, selon le type d'entrée
à définir à chaque nouvelle classe :
    _checktype
    _addition
    _multiplication

"""
import cs.parameters

class Operator(object):
    def __init__(self, operand_name, base_func,
                              constant_prop_func = None,
                              prop_func = None, unary = False):
        self.operand_name = operand_name
        self.base_func = base_func
        self.unary = unary
        if constant_prop_func is None:
            if unary:
                self.constant_prop_func = lambda x:{}
            else:
                self.constant_prop_func = lambda x,y:{}
        else:
            self.constant_prop_func = constant_prop_func
        if prop_func is None:
            self.prop_func = lambda x,y:{}
        else:
            self.prop_func = prop_func
        def inv_arg(f):
            def func(x,y):
                return f(y,x)
            return func
        self.inv_arg = inv_arg
        self.inv_constant_prop_func = inv_arg(constant_prop_func)
        self.inv_const_modified = False
        self.inv_base_func = inv_arg(base_func)
        self.inv_base_modified = False

    def set_base_func(self, func):
        '''func doit renvoyer func(self, other) = self OP other
        ou si unaire func(self)'''
        self.base_func = func
        if not self.inv_base_modified:
            self.inv_base_func = self.inv_arg(func)

    def set_const_func(self, func):
        '''func(self, other) doit renvoyer un
        dictionnaire des propriétés d'un nouvel objet
        other ne possède qu'une valeur (int ou float typiquement)
        ou si unaire func(self)'''
        self.constant_prop_func = func
        if not self.inv_const_modified:
            self.inv_const_func = self.inv_arg(func)

    def add_const_func(self, func):
        actual_func = self.constant_prop_func
        def new_func(*args):
            actual_dict = actual_func(*args)
            new_dict = func(*args)
            return {**actual_dict, **new_dict}
        self.constant_prop_func = new_func
        if not self.inv_const_modified:
            self.inv_const_func = self.inv_arg(new_func)

    def add_prop_func(self, func):
        actual_func = self.prop_func
        def new_func(*args):
            actual_dict = actual_func(*args)
            new_dict = func(*args)
            return {**actual_dict, **new_dict}
        self.prop_func = new_func
        
    def set_prop_func(self, func):
        '''func(self, other) doit renvoyer  un
        dictionnaire des propriétés de l'objet mis à jour
        other doit posséder les mêmes propriétés que self
        '''
        self.prop_func = func

    def set_inv_const_func(self, func):
        '''func(self, other) doit renvoyer  un dicitonnaire
        other ne possède qu'une valeur (int ou float typiquement)
        ou si unaire func(self)'''
        self.inv_constant_prop_func = func
        self.inv_const_modified = True

    def add_inv_const_func(self, func):
        actual_func = self.inv_constant_prop_func
        def new_func(*args):
            actual_dict = actual_func(*args)
            new_dict = func(*args)
            return {**actual_dict, **new_dict}
        self.inv_constant_prop_func = new_func
        self.inv_const_modified = True

    def set_inv_base_func(self, func):
        '''func doit renvoyer func(self, other) = other OP self
        ou si unaire func(self)'''
        self.inv_base_func = func
        self.inv_base_modified = True

class SupportedTypes(object):
    def __init__(self, add_supported_types = None, add_constant_types = None, add_converted_types = None, add_unsupported_types = None):
        self.append_type('SUPPORTED_TYPES', value = add_supported_types, set_default = True, default = (int, float, self.__class__))
        self.append_type('SUPPORTED_CONSTANT_TYPES', value = add_constant_types, set_default = True, default = (int, ))
        self.append_type('SUPPORTED_CONVERTED_TYPES', value = add_converted_types, set_default = True, default = (float, ))
        self.append_type('UNSUPPORTED_CONVERTED_TYPES', value = add_unsupported_types, set_default = True, default = (type(None), ))
    
    def append_type(self, attribute, value = None, set_default = False, default = None):
        if set_default:
            setattr(self, attribute, default)
        if value is not None:
            if type(value) is tuple:
                old_value = getattr(self, attribute)
                setattr(self, attribute, (*old_value, *value))
            else:
                old_value = getattr(self, attribute)
                setattr(self, attribute, (*old_value, value))
        
class NumericType(SupportedTypes):
    '''https://docs.python.org/3/library/numbers.html#implementing-the-arithmetic-operations'''
    def __init__(self, value, return_class = None, typename = 'Generic Numerical Class', warning = True, **kwargs):
        self.typename = typename
        self.value = value
        if return_class is None:
            return_class = self.__class__
        self.return_class = return_class
        self.warning = warning
        
        #--- OPERATIONS ---
        self.operators = {
                '+':Operator('+', lambda x,y:x+y),
                'neg':Operator('neg', lambda x:-x, unary = True),
                '*':Operator('*', lambda x,y:x*y),
                '/':Operator('/', lambda x,y:x/y),
                '//':Operator('//', lambda x,y:x//y),
                '**':Operator('**', lambda x,y:x**y),
                'abs':Operator('abs', lambda x:abs(x), unary = True),
                '=':Operator('=', lambda x,y:x==y),
                '<':Operator('<', lambda x,y:x<y)
                }

        self._setoperators()
        
        SupportedTypes.__init__(self, **kwargs)
        '''defines :
        self.SUPPORTED_TYPES = (int, float, self.__class__) #all types able to give a result
        self.SUPPORTED_CONSTANT_TYPES = (int,) #particular type
        self.SUPPORTED_CONVERTED_TYPES = (float,) #particular type needing conversion
        self.UNSUPPORTED_CONVERTED_TYPES = (type(None),) #particular type unable to make a conversion : warning - __init__ must be value only if possible
        '''
    
    def set_warning(self, w):
        self.warning = w
        
    @property
    def SUPPORTED_NUM_TYPES(self):
        return self.SUPPORTED_CONSTANT_TYPES+self.SUPPORTED_CONVERTED_TYPES
    
    def _setoperators(self):
        pass #to implement infra
    
    def _compatibility(self, x, operand, othertype, **kwargs):
        return isinstance(x, othertype)
    
    def _checktype(self, x, operand = '', force_warning = None):
        if force_warning is None:
            force_warning = self.warning
        if not self._compatibility(x, operand, self.SUPPORTED_TYPES):
            raise TypeError("Unsupported operand type for {:s}: '{:s}' and '{:s}'".format(operand, self.typename, type(x).__name__))
        if self._compatibility(x, operand, self.UNSUPPORTED_CONVERTED_TYPES):
            if force_warning and cs.parameters.WARNING:
                print("Warning [operation not supported]: type '{:s}' is lost for operand {:s}".format(self.typename, operand))
            return False
        if self._compatibility(x, operand, self.SUPPORTED_NUM_TYPES):
            return False #compatbility with calculations
        return True
    
    def _compute_return_class(self, x, operator,
                              operator_inverse = False,
                              return_class = None,
                              inplace = False):
        ''' La fonction de calcul numérique : operator.base_func(self.value,x ou x.value)
        Selon si le type de x est considéré :
                - CONSTANT : on appelle operator.constant_prop_func(x, dictionnaire des propriétés actuelles)
                            qui retourne un dictionnaire de définition du type à faire évoluer
                            pour créer un return_class
                            par défaut les propriétés sont inchangées
                - CONVERTED : on crée un nouveau return_class(x) (avec calcul auto des propriétés)
                - SINON : c'est un type du même type, on appelle operator.prop_func(self, x)
                            qui doit retourner un dictionnaire de nouvelles propriétés
                            et retourne un return_class
                            par défaut les propriétés sont laissées vides, mais c'est a priori à changer.
                - SI PAS RECONNU : retourne un type numérique de base sans rien. (warning)
                
            Options :
                operator_inverse pour définir un opérateur qui be commute pas
                return_class : par défaut c'est le return_class de la classe
                inplace : pour les opérations +=, -=... Si type pas reconnu : erreur
                
        '''
        assert not operator_inverse or not inplace #on ne peut vouloir l'opération inverse et la faire en place...
        t = self._checktype(x, operand = operator.operand_name)
        if return_class is None:
            return_class = self.return_class

        if isinstance(x, self.SUPPORTED_CONSTANT_TYPES):
            if operator_inverse:
                return return_class(operator.inv_base_func(self.value, x), **operator.inv_constant_prop_func(self, x))
            elif inplace:
                self.value = operator.base_func(self.value, x)
                return self
            else:
                return return_class(operator.base_func(self.value,x), **operator.constant_prop_func(self, x))
        elif isinstance(x, self.SUPPORTED_CONVERTED_TYPES):
            if operator_inverse:
                return operator.inv_base_func(self, return_class(x))
            elif inplace:
                return self._compute_return_class(return_class(x), operator, operator_inverse, return_class, inplace)
            else:
                return operator.base_func(self,return_class(x))
        elif t:
            if operator_inverse:
                return return_class(operator.inv_base_func(self.value, x.value), **operator.prop_func(x, self))
            elif inplace:
                self.value = operator.base_func(self.value, x)
                new_properties = operator.prop_func(self, x)
                for prop, val in new_properties:
                    setattr(self, prop, val)
                return self
            else:
                return return_class(operator.base_func(self.value,x.value), **operator.prop_func(self, x))
        else:
            if operator_inverse:
                return operator.base_func(x, self.value)
            elif inplace:
                return NotImplemented
            #Error("Erreur : perte de type.\
            #              On ne peut vouloir faire un \
            #              calcul en place ({:s}) si la conversion de type n'est pas \
            #              permise avec '{:s}'".format(operator.operand_name, type(x)))
            else:
                return operator.base_func(self.value,x)

    def _compute_return_func(self, x, operator, operator_inverse = False):
        t = self._checktype(x, operand = operator.operand_name)
        if t:
            if operator_inverse:
                return operator.base_func(x.value, self.value)
            else:
                return operator.base_func(self.value,x.value)
        else:
            if operator_inverse:
                return operator.base_func(x, self.value)
            else:
                return operator.base_func(self.value,x)

    def _compute_return_class_unaire(self, operator):
        return self.return_class(operator.base_func(self.value), **operator.constant_prop_func(self))
   
    def _addition(self, other, inplace = False):
        return self._compute_return_class(other, self.operators['+'], inplace = inplace)
        
    def _negation(self):
        return self._compute_return_class_unaire(self.operators['neg'])
        
    def _multiplication(self, other, inplace = False):
        return self._compute_return_class(other, self.operators['*'], inplace = inplace)

    def _division(self, other, operator_inverse = False, inplace = False):
        return self._compute_return_class(other, self.operators['/'], operator_inverse, inplace = inplace)

    def _division_entiere(self, other, operator_inverse = False):
        return self._compute_return_class(other, self.operators['//'], operator_inverse)

    def _puissance(self, other, operator_inverse = False):
        return self._compute_return_class(other, self.operators['**'], operator_inverse)

    def _absolue(self):
        return self._compute_return_class_unaire(self.operators['abs'])
                
    def _egalite(self, other):
        return self._compute_return_func(other, self.operators['='])
                
    def _inferieur(self, other):
        return self._compute_return_func(other, self.operators['<'])
                
    def __repr__(self):
        return repr(self.value)
    
    def __print__(self):
        return self.__repr__()

    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        """True if self != 0. Called for bool(self)."""
        return self.value != 0

    def __add__(self, x):
        """self + other"""
        return self._addition(x)

    def __radd__(self, other):
        """other + self"""
        return self + other

    def __neg__(self):
        """-self"""
        return self._negation()

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
        return self._multiplication(x)

    def __rmul__(self, other):
        """other * self"""
        return self * other #commute !

    def __truediv__(self, x):
        return self._division(x)

    def __rtruediv__(self, x):
        """other / self"""
        return self._division(x, operator_inverse = True)

    def __pow__(self, x):
        """self**exponent; should promote to float or complex when necessary."""
        return self._puissance(x)

    def __rpow__(self, x):
        """base ** self"""
        return self._puissance(x, operator_inverse = True)

    def __abs__(self):
        """Returns the Real distance from 0. Called for abs(self)."""
        return self._absolue()

    def __eq__(self, other):
        """self == other"""
        return self._egalite(other)

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
        if self.value>0:
            self.__floor__()
        elif self.value<0:
            self.__ceil__()
        else:
            return 0

    def __floor__(self):
        """Finds the greatest Integral <= self."""
        return self//1

    def __ceil__(self):
        """Finds the least Integral >= self."""
        return self//1+1

    def __round__(self, ndigits = 0):
        """Rounds self to ndigits decimal places, defaulting to 0.
        If ndigits is omitted or None, returns an Integral, otherwise
        returns a Real. Rounds half toward even.
        """
        return round(self.value, ndigits)

    def __divmod__(self, other):
        """divmod(self, other): The pair (self // other, self % other).
        Sometimes this can be computed faster than the pair of
        operations.
        """
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
        return self._division_entiere(other)

    def __rfloordiv__(self, other):
        """other // self: The int() of other/self."""
        return self._division_entiere(other, operator_inverse=True)

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
        return self._inferieur(other)

    def __le__(self, other):
        """self <= other"""
        return self < other or self==other

    def __gt__(self, other):
        """self > other
        < on Reals defines a total ordering, except perhaps for NaN."""
        return -self < -other

    def __ge__(self, other):
        """self >= other"""
        return -self <= -other

    def __complex__(self):
        """complex(self) == complex(float(self), 0)"""
        return complex(float(self))

    def __iadd__(self, x):
        return self._addition(x, inplace = True)

    def __isub__(self, x):
        self += -x
        return self

    def __imul__(self, x):
        return self._multiplication(x, inplace = True)

    def __itruediv__(self, x):
        return self._division(x, inplace = True)
