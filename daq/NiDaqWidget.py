__author__ = 'Lars Herrmann'

import pyqtgraph as pg
from PyQt4 import QtCore, QtGui, uic
import os

from pyqtgraph.dockarea import *


class NiDaqWidget(pg.LayoutWidget):

    def __init__(self):
        super(NiDaqWidget, self).__init__()
        self.ui = uic.loadUi("./panels/UiForms/SpatialLightModulatorUI.ui", self)
        self.ui.show()

if __name__ == "__main__":
    print os.getcwd()
    os.chdir('../')
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    area = DockArea()
    win.setCentralWidget(area)

    d1 = Dock("NiDaqWidget", size=(1, 1))
    area.addDock(d1)

    d1.addWidget(NiDaqWidget())
    win.show()
    app.exec_()

