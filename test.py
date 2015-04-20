__author__ = 'df-setup-basement'

import numpy as np
import timeit
import matplotlib.pyplot as plt
from detectors.spectrometers.andor.communication.AndorIdus import *

import cProfile

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func


@do_cprofile
def func():
    print ("omse function")

def func2():
    flattenarray()

def func3():
    flattenarray2()

arr = np.random.rand(5, 5)

def flattenarray():
    arr2 = arr.T
    arr2 = arr2.flatten()
    return arr2

def flattenarray2():
    tmp = np.empty((np.size(arr, 0)*np.size(arr, 1)))
    for i in range(np.size(arr, 0)):
        for j in range(np.size(arr, 1)):
            tmp[i + j*np.size(arr, 1)] = arr[i][j]
    return tmp

a1 = flattenarray()
print a1
a2 = flattenarray2()
print a2

plt.plot(a1, a2)
plt.show()

a = timeit.timeit(func2, number = 100000)
b = timeit.timeit(func3, number = 100000)

print b/a
#result = func()



