#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyqtgraph.console
from PyQt4 import Qt, QtGui, QtCore
from pyqtgraph.dockarea import *
import pickle
from panels.TimeSeries import *
from panels.SpectrometerDisplay import *
from panels.Positioning import *
from panels.ThorCam import *
from panels.GeneralControl import *
from panels.SpectrometerControl import *
from panels.StageControl import *
from panels.HistorySettings import *
from panels.HistoryDisplay import *
from panels.SLMControl import *
import ConfigParser
import daq.NiDaqControl as nidaq
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

        # ------------------------------------------------ INSTRUMENT CONTROL INSTANCES ---------------------------
        # DAQ card, channel 0 (for shutter)
        self.vo = nidaq.VoltageOutput(nidaq.NiDaqControl(), 'cDAQ1Mod1', 0, -5.0, 5.0)

        # ------------------------------------------------ DATABASE AND STORAGE CONTROL INSTANCES ---------------------------
        #if shrd.__DB__ is None:     # init if controller has not been instanced yet.
        self.db_ctrl = dbctrl.DatabaseControl()
        # initiate storage instance
        #if shrd.__STORAGE__ is None:
        self.storage_ctrl = storage.StorageControl()

        # ------------------------------------------------ BEGIN GUI Initialisation ---------------------------
        self.win = QtGui.QMainWindow()

        # disable close button
        self.win.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint
        | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

        # status bar
        self.status_bar = self.win.statusBar().showMessage("Ready")

        # menu bar
        self.menu_bar = self.win.menuBar()

        file_menu = self.menu_bar.addMenu('&Tools')

        save_dock_action = QtGui.QAction('&Save dock state', self)
        save_dock_action.setShortcut('Ctrl+D')
        save_dock_action.triggered.connect(self.store_dock_state)
        file_menu.addAction(save_dock_action)

        exit_action = QtGui.QAction('&Exit', self)
        exit_action.setShortcut('')
        exit_action.triggered.connect(self.shutdown_application)
        file_menu.addAction(exit_action)

        self.area = DockArea()
        splash.showMessage("Creating panels and docks...")

        self.win.setCentralWidget(self.area)
        self.win.showMaximized()
        self.win.setWindowTitle('Control Panel')

        # ------------------ CREATE DOCKS -----------------------------
        # general control dock
        self.general_dock = Dock("General Setttings", size=(1, 1), closable=False)
        self.area.addDock(self.general_dock, 'left')

        # spectra display dock
        self.spectra_display = Dock("Spectra", size=(1, 5), closable=False)
        self.area.addDock(self.spectra_display, "right")

        # positioning dock
        self.positioning_dock = Dock("Positioning", size=(1, 2.5), closable=False)
        self.area.addDock(self.positioning_dock, 'bottom', self.general_dock)

        # spectrometer control dock
        self.spectrometer_dock = Dock("Spectrometer", size=(1, 2), closable=False)
        self.area.addDock(self.spectrometer_dock, 'bottom', self.positioning_dock)

        # raster scan dock
        self.raster_scan_display = Dock("Raster scan", size=(1, 1), closable=False)
        self.area.addDock(self.raster_scan_display, "bottom", self.spectra_display)

        # time series dock
        self.time_series_disp = Dock("Time series", size=(1, 1), closable=False)
        self.area.addDock(self.time_series_disp, "above", self.raster_scan_display)

        # SLM docks
        self.slm_dock = Dock("SLM", size=(1, 1), closable=False)
        self.area.addDock(self.slm_dock, "above", self.raster_scan_display)

        # camera display docks
        self.camera_display_1 = Dock("Camera 1", size=(1, 1), closable=False)
        self.camera_display_2 = Dock("Camera 2", size=(1, 1), closable=False)

        # History dock
        self.history_display_dock = Dock("History", size=(1, 1), closable=False)
        self.area.addDock(self.history_display_dock, "right")
        self.history_settings_dock = Dock("History Settings", size=(1, 1), closable=False)
        self.area.addDock(self.history_settings_dock, "right")

        # ------------------ ADD PANELS TO DOCK -----------------------------
        # add general control to dock
        self.general_dock.addWidget(GeneralControl(self.vo, self.db_ctrl))

        # add spectra display panel to dock
        splash.showMessage("Creating panels...(Spectra display)")
        self.spectra_panel = SpectrometerDisplay()
        self.spectra_display.addWidget(self.spectra_panel)

        # add time series panel to dock
        splash.showMessage("Creating panels... (Time series)")
        self.time_series_panel = TimeSeries()
        self.time_series_disp.addWidget(self.time_series_panel)

        # add spectrometer control panel to dock
        splash.showMessage("Creating panels... (Spectrometer)")
        self.spectrometer_ctrl = SpectrometerControl(self.spectra_panel, self.time_series_panel,
                                                     self.storage_ctrl, self.vo, self.status_bar)
        self.spectrometer_dock.addWidget(self.spectrometer_ctrl)

        # add positioning control panel to dock
        splash.showMessage("Creating panels...(Positioning)")
        self.positioning_ctrl = Positioning(self.spectrometer_ctrl)
        self.positioning_dock.addWidget(self.positioning_ctrl)

        # add camera panels to dock
        splash.showMessage("Creating panels... (Camera)")
        self.area.addDock(self.camera_display_1, "bottom", self.raster_scan_display)
        self.camera1 = ThorCam()
        self.camera_display_1.addWidget(self.camera1)
        self.area.addDock(self.camera_display_2, "above", self.camera_display_1)

        # add raster scan panel to dock
        splash.showMessage("Creating panels... (Raster scan)")
        self.stage_ctrl = StageControl(self.spectrometer_ctrl, self.positioning_ctrl, self.camera1)
        self.raster_scan_display.addWidget(self.stage_ctrl)
        # now make spectrometer aware of the initialised instance
        self.spectrometer_ctrl.init_stage_interaction(self.stage_ctrl)

        # add slm control panels to dock
        splash.showMessage("Creating panels... (SLM)")
        self.slm_control = SLMControl()
        self.slm_dock.addWidget(self.slm_control)

        # add history control to dock
        splash.showMessage("Creating panels... (History)")
        self.history_display = HistoryDisplay()
        self.history_settings = HistorySettings(self.db_ctrl, self.storage_ctrl, self.history_display)
        self.history_display_dock.addWidget(self.history_display)
        self.history_settings_dock.addWidget(self.history_settings)


        # ------------------------------------------------END GUI Initialisation ---------------------------

        # load dock configuration
        self.dock_configuration = None
        self.load_config()

        if self.dock_configuration is not None:
            self.area.restoreState(self.dock_configuration)

        # style sheets

        #sshFile = "./darkorange.stylesheet"
        #with open(sshFile, "r") as fh:
        #    self.setStyleSheet(fh.read())
        #self.win.showFullScreen()
        # initiate database instance

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
