__author__ = 'df-setup-basement'


import sys
from PyQt4 import QtCore, QtGui, uic


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.Main_Window = uic.loadUi("./UiForms/PositioningUI.ui")
        self.Main_Window.show()


app = QtGui.QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())