__author__ = 'df-setup-basement'
import numpy as np

a = np.random.rand(2000)
R = 1
b = a.reshape(-1, R).mean(axis=1)

print len(b)-len(a)

