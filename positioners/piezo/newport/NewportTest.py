__author__ = 'df-setup-basement'

from positioners.piezo.newport.NewportControl import *

controlNewport = NewportControl('169.254.169.20', 23)

# move up
controlNewport.move(1, 0, 100)



