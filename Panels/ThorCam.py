__author__ = 'df-setup-basement'

from PyQt4 import uic
from PyQt4.QtGui import *

from detectors.cameras.thorlabs.communication.ThorcamControl import *


class ThorCam(pg.LayoutWidget):

    def __init__(self):
        super(ThorCam, self).__init__()
        self.ui = uic.loadUi("./Panels/UiForms/ThorCamUI.ui",self)
        self.ui.show()

        win = pg.GraphicsLayoutWidget()
        view = win.addViewBox()
        win.show()
        self.video_stream = pg.ImageItem(border='w')
        self.video_stream.setAutoDownsample(True)
        view.addItem(self.video_stream)
        box_layout = QHBoxLayout()
        box_layout.addWidget(win)
        self.ui.frame.setLayout(box_layout)

        # Gradient editor to manipulate color levels (look up table)
        gradient_win = pg.GraphicsLayoutWidget()
        gradient_view = gradient_win.addViewBox()
        gradient_win.show()
        self.gradient_editor = pg.GradientEditorItem()
        self.gradient_editor.loadPreset('grey')
        gradient_view.addItem(self.gradient_editor)
        box_layout_grad = QHBoxLayout()
        box_layout_grad.addWidget(gradient_win)
        gradient_win.setCentralItem(self.gradient_editor)
        self.ui.gradientframe.setLayout(box_layout_grad)

        # event handling

        # initialise camera
        self.connect(self.ui.b_init, QtCore.SIGNAL("clicked()"), self.init_camera)

        # streaming & snapshots
        self.connect(self.ui.b_play, QtCore.SIGNAL("clicked()"), self.update_data)
        self.streaming_status = False
        self.connect(self.ui.b_capture, QtCore.SIGNAL("clicked()"), self.capture_image)

        # exposure & gain
        self.ui.t_exp.valueChanged[str].connect(self.adjust_exp)
        self.ui.t_gain.valueChanged[str].connect(self.adjust_gain)

        # colors & filters
        self.ui.rb_gray.toggled.connect(self.toggle_gray_rgb)
        self.ui.c_isPSD.stateChanged.connect(self.toggle_psd)

        # export image
        self.connect(self.ui.b_store, QtCore.SIGNAL("clicked()"), self.store_image)

        # initialise instances
        self.thorcam = 0
        self.initStatus = 0

    def init_camera(self):
        self.thorcam = ThorcamControl(self.video_stream, self.gradient_editor)
        self.initStatus = 1
        self.ui.b_play.setDisabled(False)
        self.ui.b_capture.setDisabled(False)
        self.ui.b_store.setDisabled(False)
        self.ui.b_init.setDisabled(True)
        self.ui.rb_rgb.setDisabled(False)
        self.ui.rb_gray.setDisabled(False)
        self.ui.c_isPSD.setDisabled(False)
        self.ui.t_exp.setDisabled(False)
        self.ui.t_gain.setDisabled(False)
        print "Camera intitialised."

    def capture_image(self):
        if self.initStatus:
            self.thorcam.snap()

    def store_image(self):
        if self.initStatus:
            self.thorcam.store()

    def update_data(self):
        if self.initStatus and not self.streaming_status:
            self.ui.b_capture.setDisabled(True)
            self.thorcam.run()
            self.streaming_status=True
        elif self.initStatus and self.streaming_status:
            self.ui.b_capture.setDisabled(False)
            self.thorcam.pause()
            self.streaming_status=False
        else:
            print "Please initialise camera."

    def adjust_exp(self):
        if self.initStatus:
            self.thorcam.exposure(self.ui.t_exp.value())

    def adjust_gain(self):
        if self.initStatus:
            self.thorcam.gain(self.ui.t_gain.value())

    def toggle_psd(self):
        self.thorcam.toggle_psd()

    def toggle_gray_rgb(self):
        self.thorcam.toggle_gray_rgb()