__author__ = 'df-setup-basement'

import numpy as np
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from detectors.spectrometers.andor.communication.Shamrock import *
from detectors.spectrometers.andor.communication.AndorIdus import *


class SaveFile(QtGui.QMainWindow):

    def __init__(self, arr):
        super(SaveFile, self).__init__()
        self.arr = arr
        self.init_dialog()

    def init_dialog(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '')
        filename += ".txt"
        filename = os.path.abspath(filename)
        with file(filename, 'w') as outfile:
            np.savetxt(outfile, self.arr, delimiter='\t')

def dark_noise():
    filename = "C:\\Users\\df-setup-basement\\Desktop\\"
    shamrock = Shamrock()
    shamrock.set_wavelength_absolute(800)
    print shamrock.get_grating_choices()

    #shamrock.shutter_control(0)
    andor = AndorIdus()
    andor.set_single_fvb()
    shamrock.set_number_pixels(andor._width)
    shamrock.set_pixel_width(andor._pixel_width)
    calibration = shamrock.get_calibration(andor._width)
    print calibration

    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)


    print andor.get_temperature()

    average = 4        # number of spectra to average over
    temperature = [-65]
    int_times = np.logspace(-1, 1, 10, endpoint=True)
    av_counts = np.empty((np.size(int_times, 0)))

    print ("Starting to cool down to " + str(temperature[0]) + " C")
    #andor.cool_down(temperature[0])
    print ("Cooled down to: ")
    print andor.get_temperature()
    counts_av = []
    array = np.empty((np.size(calibration, 0), np.size(int_times, 0)+1))
    for k in range(np.size(calibration, 0)):
        array[k][0] = calibration[k]
    for i in range(np.size(int_times, 0)):        # iterate over exposure times
        andor.set_exposure_time(int_times[i])
        av = 0
        counts_wl = np.empty(andor._width)
        for j in range(average):
            data = []
            andor.start_acquisition()
            andor.wait_for_acquisition()
            andor.get_acquired_data(data)
            for p in range(np.size(data, 0)):
                counts_wl[p] += float(data[p])/average
            av += np.average(data)
        for k in range(np.size(counts_wl, 0)):
            array[k][i+1] = counts_wl[k]
        counts_av.append(av)
        print ("integration time " + str(i))


    # save data
    print("save data")
    with file(filename + "N_OD3L15_sig_1.txt", 'w') as outfile:
            np.savetxt(outfile, array, delimiter='\t')
    with file(filename + "N_OD3L15_sig_int_time_1.txt", 'w') as outfile:
            np.savetxt(outfile, int_times, delimiter='\t')
    with file(filename + "N_OD3L15_sig_counts_1.txt", 'w') as outfile:
            np.savetxt(outfile, counts_av, delimiter='\t')

    shamrock.close()
    andor.shutdown()


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        print  np.logspace(-1, 1, 8, endpoint=True)
        dark_noise()
        #QtGui.QApplication.instance().exec_()










