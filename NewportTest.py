__author__ = 'df-setup-basement'

from NewportControl import *
import ctypes
import time

controlNewport = NewportControl('169.254.169.20', 23)

# move up
controlNewport.move(1, 0, 100)



