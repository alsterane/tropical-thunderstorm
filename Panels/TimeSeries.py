__author__ = 'df-setup-basement'

from PyQt4 import uic, QtCore, QtGui
import pyqtgraph as pg
import numpy as np

class TimeSeries(pg.ImageView):

    def __init__(self):
        ## Create window with ImageView widget
        super(TimeSeries, self).__init__()
        self.resize(800,800)
        self.show()
        ## Create random 3D data set with noisy signals
        img = pg.gaussianFilter(np.random.normal(size=(200, 200)), (5, 5)) * 20 + 100
        img = img[np.newaxis,:,:]
        decay = np.exp(-np.linspace(0,0.3,100))[:,np.newaxis,np.newaxis]
        data = np.random.normal(size=(100, 200, 200))
        data += img * decay
        data += 2

        ## Add time-varying signal
        sig = np.zeros(data.shape[0])
        sig[30:] += np.exp(-np.linspace(1,10, 70))
        sig[40:] += np.exp(-np.linspace(1,10, 60))
        sig[70:] += np.exp(-np.linspace(1,10, 30))

        sig = sig[:,np.newaxis,np.newaxis] * 3
        data[:,50:60,50:60] += sig


        ## Display the data and assign each frame a time value from 1.0 to 3.0
        self.setImage(data, xvals=np.linspace(1., 3., data.shape[0]))