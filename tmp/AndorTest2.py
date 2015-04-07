
from detectors.spectrometers.andor.communication.AndorIdus import *

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *

""" show real time data acquisition and plotting """


class SpectraDisplay(pg.LayoutWidget):

    def __init__(self):
        super(SpectraDisplay, self).__init__()
        self.lplt = pg.PlotWidget()
        self.addWidget(self.lplt)
        self.andor = AndorIdus()
        # full vertical binning mode
        self.andor.set_read_mode(0)
        self.andor.set_exposure_time(0.1)

    def stream(self):
        """
        Fetch data and send to plot.

        :return:
        """
        data = []   # to store array data
        self.andor.get_most_recent_image(data)
        self.lplt.plot(data, clear=True)

    def live_stream(self, cycle_time):
        """
        Start a 'Run till abort' acquisition and constantly update spectra display.

        :param cycle_time: int Minimal time between two acquisitions.
        :return:
        """
        print "run viewtimer"
        global view_timer

        # set parameters to run till abort mode
        self.andor.set_acquisition_mode(5)

        # minimal kinetic cycle time
        self.andor.set_kinetic_cycle_time(cycle_time)

        self.andor.start_acquisition()
        view_timer = QtCore.QTimer()
        view_timer.timeout.connect(self.stream)
        view_timer.start(0)

    def pause(self):
        """
        Pauses the currently ongoing 'Run till abort'-acquisition.

        :return:
        """
        if view_timer.isActive():
            self.andor.abort_acquisition()
            view_timer.stop()



# code to test the class above
def main():

    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    area = DockArea()
    win.show()


    win.setCentralWidget(area)
    win.resize(1000, 500)
    win.setWindowTitle('Control Panel')

    spectraDock = Dock("Spectra", size=(1, 1.5))
    area.addDock(spectraDock, 'left')
    sDisp = SpectraDisplay()
    spectraDock.addWidget(sDisp)
    sDisp.run()


    QtGui.QApplication.instance().exec_()

if  __name__ =='__main__':main()