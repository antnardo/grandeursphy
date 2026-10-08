#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 22:53:31 2017

@author: elessar

CS module tests
"""
import cs
from cs import CS, CTES, SI
cs.set_confiance(2)
cs.set_warnings(False)

print(CTES['c'])

#Final tests
c = CS(299792458)
print('c :', c)
b = CS(3e-4)
print('b :', b)
v = (b+1)*c
print('v :', v)
div = v//2
print('div :', div)
d = v%2
print('d :', d)

a = CS(1)
print(a, a//2)
