import pyorcy
import numpy as np
#c cimport cython

def value(i, j, price, amount): #p
#c @cython.boundscheck(False)
#c cdef double value(int i, int j, double[:] price, double[:] amount):
    #c cdef int a, p
    #c cdef double v
    v = price[i] * amount[j]
    return v

@pyorcy.cythonize #p
def f(n, m): #p
#c def f(int n, int m):
    #c cdef int i, j
    #c cdef double v
    #c cdef double[:] price
    #c cdef double[:] amount
    price = np.linspace(1, 2, n)
    amount = np.linspace(3, 4, m)
    v = 0
    for i in range(n):
        for j in range(m):
            v += value(i, j, price, amount)
    return v
