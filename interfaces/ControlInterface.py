__author__ = 'df-setup-basement'


#from pyqtgraph.Qt import QtCore, QtGui

import numpy as np
from pyqtgraph.dockarea import *
import pyqtgraph as pg
import pyqtgraph.console

from Panels.TimeSeries import *
from Panels.Spectra import *
from Panels.RasterScan import *
from Panels.Positioning import *
from Panels.ThorCam import *
from Panels.LaserControl import *
from Panels.SpectrometerControl import *
from Panels.SLMControl import *

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
area = DockArea()

sshFile="./dark.stylesheet"
with open(sshFile, "r") as fh:
    win.setStyleSheet(fh.read())

win.setCentralWidget(area)
win.resize(1000, 500)
win.setWindowTitle('Control Panel')

# control shutter and laser
laserDock = Dock("Laser", size=(1, 1.5))
area.addDock(laserDock, 'left')
laserDock.addWidget(LaserControl())

# control positioners of sample and objectives
positioningDock = Dock("Positioning", size=(1, 3), closable=False)
area.addDock(positioningDock, 'bottom', laserDock)
madCityPanel = MadCity()
positioningDock.addWidget(madCityPanel)

# SPECTROMETER CONTROL PANEL
spectrometerDock = Dock("Spectrometer", size=(1, 2))
area.addDock(spectrometerDock, 'bottom', positioningDock)
spectrometerDock.addWidget(SpectrometerControl())

# CONSOLE
consoleDock = Dock("Console", size=(1, 2), closable=False)
area.addDock(consoleDock, 'bottom', spectrometerDock)
consolePanel = pg.console.ConsoleWidget()
#consolePanel.catchAllExceptions(catch=True)
consoleDock.addWidget(consolePanel)


# SPECTRA DISPLAY PANEL
spectraDisplay = Dock("Spectra", size=(1, 2))
area.addDock(spectraDisplay, "right")
spectraPanel = Spectra()
spectraDisplay.addWidget(spectraPanel)

# RASTER SCAN PANEL
rasterScanDisplay = Dock("Raster scan", size=(1, 1))
area.addDock(rasterScanDisplay, "bottom", spectraDisplay)
rasterScanPanel = RasterScan()
rasterScanDisplay.addWidget(rasterScanPanel)

# TIME SERIES PANELS
timeSeriesDisplay = Dock("Time series", size=(1, 1))
area.addDock(timeSeriesDisplay, "above", rasterScanDisplay)
timeSeriesPanel = TimeSeries()
timeSeriesDisplay.addWidget(timeSeriesPanel)

# SLM CONTROL PANEL
slmDock = Dock("SLM", size=(1, 1))
area.addDock(slmDock, "above", rasterScanDisplay)
slmDock.addWidget(SLMControl())

# CAMERA DISPLAY PANELS
cameraDisplay1 = Dock("Camera 1", size=(1, 1))
area.addDock(cameraDisplay1, "bottom", rasterScanDisplay)
cameraDisplay1.addWidget(ThorCam())
cameraDisplay2 = Dock("Camera 2", size=(1, 1))
area.addDock(cameraDisplay2, "above", cameraDisplay1)

win.show()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
