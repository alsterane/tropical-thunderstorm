

from detectors.spectrometers.andor.communication.Shamrock import *
from detectors.spectrometers.andor.communication.AndorIdus import *
import timeit
import matplotlib.pyplot as plt

andor = AndorIdus()

def func():
    andor.start_acquisition()
    andor.wait_for_acquisition()
    data2 = andor.get_acquired_data_fast()

# take a single fvb image
andor.set_acquisition_mode(1)
andor.set_single_fvb()
#andor.set_exposure_time(0)
andor.get_acquisition_timings()
print andor._exposure
#print timeit.timeit(func, number=20)

andor.set_read_mode(4)
andor.set_acquisition_mode(1)
andor.set_vb_image(1, 1, 2000, 1, 256)
andor.get_acquisition_timings()
print andor._exposure
#print timeit.timeit(func, number=20)




#plt.plot(data)
#plt.plot(data2)
#plt.show()

andor.shutdown()

