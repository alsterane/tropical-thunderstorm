__author__ = 'df-setup-basement'

from PyQt4 import uic
import pyqtgraph as pg
from PyQt4.QtGui import *


class SLMControl (pg.LayoutWidget):

    def __init__(self):
        super(SLMControl, self).__init__()
        self.ui = uic.loadUi("./Panels/UiForms/SpatialLightModulatorUI.ui", self)
        self.ui.show()

        # laser_monitor = pg.PlotWidget(name='Plot1')
        # laser_monitor.setLabel('bottom', 'time (s)')
        # laser_monitor.setLabel('left', 'counts', units=None)
        # laser_monitor.showAxis('right', show=True)
        # laser_monitor.showAxis('top', show=True)
        # laser_monitor.enableAutoScale()
        # box_layout = QHBoxLayout()
        # box_layout.addWidget(laser_monitor)
        # self.ui.frame.setLayout(box_layout)

