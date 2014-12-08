
import numpy as np
from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from PyQt4 import *
app = QtGui.QApplication([])

def updateview():
    global img, camera
    data = np.random.normal(size=(5, 300, 300), loc=1024, scale=64).astype(np.uint16)
    img.setImage(data[0])

win = QtGui.QWidget()

# Image widget
imagewidget = pg.GraphicsLayoutWidget()
view = imagewidget.addViewBox()
view.setAspectLocked(True)
img = pg.ImageItem(border='w')
view.addItem(img)
view.setRange(QtCore.QRectF(0, 0, 512, 512))

layout = QtGui.QGridLayout()
win.setLayout(layout)
layout.addWidget(imagewidget, 1, 2, 3, 1)
win.show()

viewtimer = QtCore.QTimer()
viewtimer.timeout.connect(updateview)
viewtimer.start(0)

app.exec_()
viewtimer.stop()