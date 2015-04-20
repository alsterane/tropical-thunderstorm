__author__ = 'df-setup-basement'

from detectors.spectrometers.andor.communication.AndorIdus import *

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np



# initialise spectrometer
andor = AndorIdus()
print("Serial number is: %s" % andor.get_camera_serial_number())
#
print("Temperature is: %s" % andor.get_temperature())
#
# set exposure time
#
# # apply single fvb scan settings
#andor.set_single_fvb()
#data = andor.capture_fvb()

andor.set_acquisition_mode(1)
andor.set_read_mode(0)
andor.set_exposure_time(.3)
#andor.set_kinetic_cycle_time(0.5)
#
andor.start_acquisition()

data = []
data = andor.get_acquired_data_fast(data)

print np.shape(data)
plt.plot(data)
plt.show()

andor.abort_acquisition()

#
# # shutdown spectrometer
andor.__del__()

