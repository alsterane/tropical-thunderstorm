__author__ = 'df-setup-basement'

from PyQt4 import uic
import pyqtgraph as pg
from PyQt4.QtGui import *


class SpectrometerControl(pg.LayoutWidget):

    def __init__(self):
        super(SpectrometerControl, self).__init__()
        self.ui = uic.loadUi("./Panels/UiForms/SpectrometerControlUI.ui", self)
        self.ui.show()
