__author__ = 'df-setup-basement'

import sys
from PyQt4 import QtGui
from PIL import Image
import numpy as np
import os


class SaveImage(QtGui.QMainWindow):

    def __init__(self, img):
        super(SaveImage, self).__init__()
        self.img = img
        self.init_dialog()

    def init_dialog(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '')
        rescaled = (255.0 / self.img.max() * (self.img - self.img.min())).astype(np.uint8)
        im = Image.fromarray(rescaled)
        filename += ".jpg"
        filename = os.path.abspath(filename)
        im.save(filename, format="JPEG")