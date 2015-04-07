#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyqtgraph.console
from PyQt4 import Qt, QtGui, QtCore
import pickle
from panels.TimeSeries import *
from panels.SpectrometerDisplay import *
from panels.Positioning import *
from panels.ThorCam import *
from panels.GeneralControl import *
from panels.SpectrometerControl import *
from panels.StageControl import *
from panels.HistoryDisplay import *
from panels.SLMControl import *
import ConfigParser
import SharedDefinitions as shrd
import storage.DatabaseControl as dbctrl
import storage.StorageControl as storage


class Interface(QtGui.QApplication):

    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)

        # Create and display the splash screen
        splash_pix = QtGui.QPixmap('./panels/splash_screen/splash.png')
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        self.processEvents()
        splash.showMessage("Loading configuration...")

        # ------------------------------------------------BEGIN GUI Initialisation ---------------------------
        self.win = QtGui.QMainWindow()

        # disable close button
        self.win.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint
        | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

        # statusbar
        self.statusbar = self.win.statusBar().showMessage("Ready")

        # menubar
        self.menubar = self.win.menuBar()

        file_menu = self.menubar.addMenu('&Tools')

        save_dock_action = QtGui.QAction('&Save dock state', self)
        save_dock_action.setShortcut('Ctrl+D')
        save_dock_action.triggered.connect(self.store_dock_state)
        file_menu.addAction(save_dock_action)

        exit_action = QtGui.QAction('&Exit', self)
        exit_action.setShortcut('')
        exit_action.triggered.connect(self.shutdown_application)
        file_menu.addAction(exit_action)

        self.area = DockArea()
        splash.showMessage("Creating panels...")

        self.win.setCentralWidget(self.area)
        self.win.showMaximized()
        self.win.setWindowTitle('Control Panel')

        # control shutter and laser
        self.general_dock = Dock("General Setttings", size=(1, 1), closable=False)
        self.area.addDock(self.general_dock, 'left')
        self.general_dock.addWidget(GeneralControl())

        # control petitioners of sample and objectives
        splash.showMessage("Creating panels...(Positioning)")
        self.positioning_dock = Dock("Positioning", size=(1, 2.5), closable=False)
        self.area.addDock(self.positioning_dock, 'bottom', self.general_dock)
        self.positioning_dock.addWidget(Positioning())

        # SPECTRA DISPLAY PANEL
        splash.showMessage("Creating panels...(Spectra display)")
        self.spectra_display = Dock("Spectra", size=(1, 5), closable=False)
        self.area.addDock(self.spectra_display, "right")
        self.spectra_panel = SpectrometerDisplay()
        self.spectra_display.addWidget(self.spectra_panel)

        # RASTER SCAN PANEL/ STAGE CONTROL PANEL
        splash.showMessage("Creating panels... (Raster scan)")
        self.raster_scan_disp = Dock("Raster scan", size=(1, 1), closable=False)
        self.area.addDock(self.raster_scan_disp, "bottom", self.spectra_display)
        self.raster_scan_panel = StageControl()
        shrd.__STAGE_CONTROL__ = self.raster_scan_panel
        self.raster_scan_disp.addWidget(self.raster_scan_panel)

        # TIME SERIES PANELS
        splash.showMessage("Creating panels... (Kinetic)")
        self.time_series_disp = Dock("Time series", size=(1, 1), closable=False)
        self.area.addDock(self.time_series_disp, "above", self.raster_scan_disp)
        self.time_series_panel = TimeSeries()
        self.time_series_disp.addWidget(self.time_series_panel)

        # SPECTROMETER CONTROL PANEL
        splash.showMessage("Creating panels... (Spectrometer)")
        self.spectrometer_dock = Dock("Spectrometer", size=(1, 2), closable=False)
        self.area.addDock(self.spectrometer_dock, 'bottom', self.positioning_dock)
        self.spectrometer = SpectrometerControl(self.spectra_panel, self.time_series_panel)
        shrd.__SPECTROMETER__ = self.spectrometer
        self.spectrometer_dock.addWidget(self.spectrometer)

        # SLM CONTROL PANEL
        splash.showMessage("Creating panels... (SLM)")
        self.slm_dock = Dock("SLM", size=(1, 1), closable=False)
        self.area.addDock(self.slm_dock, "above", self.raster_scan_disp)
        self.slm_control = SLMControl()
        self.slm_dock.addWidget(self.slm_control)

        # CAMERA DISPLAY PANELS
        splash.showMessage("Creating panels... (Camera)")
        self.camera_display_1 = Dock("Camera 1", size=(1, 1), closable=False)
        self.area.addDock(self.camera_display_1, "bottom", self.raster_scan_disp)
        shrd.__CAM1__ = ThorCam()
        self.camera_display_1.addWidget(shrd.__CAM1__)
        self.camera_display_2 = Dock("Camera 2", size=(1, 1), closable=False)
        self.area.addDock(self.camera_display_2, "above", self.camera_display_1)

        # HISTORY PANEL
        splash.showMessage("Creating panels... (History)")
        self.spectra_history = Dock("Spectra history", size=(1, 1), closable=False)
        self.area.addDock(self.spectra_history, "right")
        shrd.__HISTORY_DISPLAY__ = HistoryDisplay()
        self.spectra_history.addWidget(shrd.__HISTORY_DISPLAY__)
        # ------------------------------------------------END GUI Initialisation ---------------------------

        self.dock_configuration = None      # dock configuration if stored
        self.load_config()

        if self.dock_configuration is not None:
            self.area.restoreState(self.dock_configuration)

        #sshFile = "./darkorange.stylesheet"
        #with open(sshFile, "r") as fh:
        #    self.setStyleSheet(fh.read())
        #self.win.showFullScreen()
        # initiate database instance
        if shrd.__DB__ is None:     # init if controller has not been instanced yet.
            shrd.__DB__ = dbctrl.DatabaseControl()
        # initiate storage instance
        if shrd.__STORAGE__ is None:
            shrd.__STORAGE__ = storage.StorageControl()

        splash.finish(self.win)
        self.win.show()
        sys.exit(self.exec_())


    def load_config(self):
        """
        If a configuration file exists, then load it and assign parameters.
        """
        if os.path.exists('./data_structure_config.ini'):
            config = ConfigParser.ConfigParser()
            config.read('./data_structure_config.ini')
            shrd.__DATA_ROOT__ = config.get('root_structure', 'data_root')
            shrd.__DB_PATH__ = config.get('root_structure', 'database_path')
        if os.path.exists('./dock_configuration.ini'):
            self.dock_configuration = pickle.load(open("./dock_configuration.ini", "rb"))

    def store_dock_state(self):
        """
        Stores the current dock state in the configuration file.
        """
        state = self.area.saveState()
        f = open("./dock_configuration.ini", "wb")
        pickle.dump(state, f)

    def shutdown_application(self):
        """
        Shuts down the program.
        :return:
        """
        # TODO: Implement proper shutdown of all the instances that are running".
        msg_box = QtGui.QMessageBox(QMessageBox.Warning, "...",  'Are you sure you want to close the application?')
        msg_box.setWindowTitle("Close")
        msg_box.addButton(QtGui.QPushButton('Yes'), QtGui.QMessageBox.YesRole)
        msg_box.addButton(QtGui.QPushButton('No'), QtGui.QMessageBox.NoRole)
        ret = msg_box.exec_()
        if not ret:
            print("Initiate shutdown process.")
            self.closeAllWindows()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        interface = Interface(sys.argv)
