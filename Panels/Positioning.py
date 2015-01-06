__author__ = 'df-setup-basement'

from PyQt4 import uic, QtCore

from pyqtgraph.dockarea import *
import pyqtgraph as pg
from positioners.piezo.madcitylabs.communication.MadCityControl import *


class MadCity(pg.LayoutWidget):
    
    def __init__(self):
        super(MadCity, self).__init__()
        self.ui = uic.loadUi("./Panels/UiForms/PositioningUI.ui",self)
        self.ui.show()

        # MadCity - Initialisation
        self.stage_handle = MadCityControl
        self.connect(self.ui.b_init, QtCore.SIGNAL("clicked()"), self.init_madcity)

        # MadCity - Parameters
        self.madcity_step = 100 #in nm
        self.ui.t_np_steps.setText(str(self.madcity_step))
        # self.connect(self.ui.t_np_steps, QtCore.SIGNAL(), self.update_steps)

        # MadCity - Steps
        self.connect(self.ui.b_np_step1, QtCore.SIGNAL("clicked()"), self.set_b_np_step1)
        self.connect(self.ui.b_np_step2, QtCore.SIGNAL("clicked()"), self.set_b_np_step2)
        self.connect(self.ui.b_np_step3, QtCore.SIGNAL("clicked()"), self.set_b_np_step3)
        self.connect(self.ui.b_np_step4, QtCore.SIGNAL("clicked()"), self.set_b_np_step4)
        self.connect(self.ui.b_np_step5, QtCore.SIGNAL("clicked()"), self.set_b_np_step5)
        self.connect(self.ui.b_np_step6, QtCore.SIGNAL("clicked()"), self.set_b_np_step6)

        # MadCity - Movement
        self.stage_handle = MadCityControl
        self.connect(self.ui.b_np_n, QtCore.SIGNAL("clicked()"), self.mv_b_np_n)

        # Lock/unlock references
        self.connect(self.checkBox_ref, QtCore.SIGNAL("clicked()"), self.lock_refs)

    # INIT MAD CITY STAGE
    def init_madcity(self):
        self.stage_handle.initialise_stage()
        print "Initialise MadCityLabs stage"

    # STEPS BUTTONS FOR MAD CITY STAGE
    def set_b_np_step1(self):
        self.ui.t_np_steps.setText(str(50))
    def set_b_np_step2(self):
        self.ui.t_np_steps.setText(str(100))
    def set_b_np_step3(self):
        self.ui.t_np_steps.setText(str(200))
    def set_b_np_step4(self):
        self.ui.t_np_steps.setText(str(500))
    def set_b_np_step5(self):
        self.ui.t_np_steps.setText(str(1000))
    def set_b_np_step6(self):
        self.ui.t_np_steps.setText(str(2000))

    # MOVEMENT OF MAD CITY STAGE
    def mv_b_np_n(self):
        distance = float(self.ui.t_np_steps.displayText())
        #self.stage_handle.move_stage()
    def mv_b_np_ne(self):
        distance = float(self.ui.t_np_steps.displayText())
    def mv_b_np_e(self):
        distance = float(self.ui.t_np_steps.displayText())
    def mv_b_np_se(self):
        distance = float(self.ui.t_np_steps.displayText())
    def mv_b_np_s(self):
        distance = float(self.ui.t_np_steps.displayText())
    def mv_b_np_sw(self):
        distance = float(self.ui.t_np_steps.displayText())
    def mv_b_np_w(self):
        distance = float(self.ui.t_np_steps.displayText())
    def mv_b_np_nw(self):
        distance = float(self.ui.t_np_steps.displayText())

    # UNLOCK/LOCK REFERENCES

    def lock_refs(self):
        if self.checkBox_ref.isChecked():
            self.b_sample_ref.setDisabled(True)
            self.b_obj1_z_ref.setDisabled(True)
            self.b_obj2_z_ref.setDisabled(True)
            self.b_obj2_xy_ref.setDisabled(True)
        else:
            self.b_sample_ref.setDisabled(False)
            self.b_obj1_z_ref.setDisabled(False)
            self.b_obj2_z_ref.setDisabled(False)
            self.b_obj2_xy_ref.setDisabled(False)



