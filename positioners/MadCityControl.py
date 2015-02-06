__author__ = 'df-setup-basement'

import ctypes
from PyQt4 import QtGui
import os

# control MadCityLabs Piezo Stage through Madlib.dll
class MadCityControl:
    """
    .. module:: MadCityControl
    :platform: Windows
    :synopsis: Module to communicate with Mad City Lab stages via Madlib.dll. Current implementation for XY stage.

    .. moduleauthor:: lh
    """

    def __init__(self):
        lib = ctypes.WinDLL('./positioners/dll/Madlib.dll')
        # gets handle to first connected stage that system finds args=()
        self.initHandle = lib['MCL_InitHandle']
        self.handle = 0

        # print device info of device with handle given by int args=(INT handle)
        self.printInfo = lib['MCL_PrintDeviceInfo']

        # return serial number args=(INT handle)
        self.getSerial = lib['MCL_GetSerialNumber']

        # disconnect stage, i.e. release handle args=(INT handle)
        self.disconnect = lib['MCL_ReleaseHandle']

        # move stage axis to specified position args=(DOUBLE position, UINT axis, INT handle)
        self.move = lib['MCL_SingleWriteN']
        self.move.restype = ctypes.c_double

        # read stage position args=(INT axis, INT handle)
        self.getPosition = lib['MCL_SingleReadN']
        self.getPosition.restype = ctypes.c_double

        # params
        self._RANGE = 100.0     # range of stage in micrometres

    # grabs the handle to the stage
    def initialise_stage(self):
        """
        Initialises Mad City Lab stage and assigns a handle to it.
        """
        self.handle = self.initHandle()
        if self.handle == 0:
            print "Stage could not be found."
            return 0
        else:
            self.printInfo(self.handle)
            print "Serial number of stage is: " + str(self.getSerial(self.handle))
            self.center_stage()
            return 1

    # releases the handle
    def disconnect_stage(self):
        """
        Disconnects from Mad City Lab stage and releases the handle to it.
        """
        self.disconnect(self.handle)

    # move stage to position along axis
    def move_stage_abs(self, abs_pos, axis):
        """
        Moves the stage to specified position along specified axis.

        :param double Position to move to.
        :param int Specifies axis to move (1=x, 2=y)
        """
        if 0.0 <= abs_pos <= self._RANGE:
            self.move(ctypes.c_double(abs_pos), axis, self.handle)
        else:
            box = QtGui.QMessageBox()
            QtGui.QMessageBox.warning(box, "Warning",
                                      "Stage limits reached. Axis " + str(axis) + ", Pos: " + str(abs_pos),
                                      QtGui.QMessageBox.Ok)
            return 0

    def move_stage_rel(self, shift, axis):
        """
        Moves the stage to specified position along specified axis.

        :param shift: Relative distance to move.
        :param int Specifies axis to move (1=x, 2=y)
        """
        abs_pos = self.read_stage(axis) + shift
        print shift
        if 0.0 <= abs_pos <= self._RANGE:
            self.move(ctypes.c_double(abs_pos), axis, self.handle)
        else:
            box = QtGui.QMessageBox()
            QtGui.QMessageBox.warning(box, "Warning",
                                      "Stage limits reached.",
                                      QtGui.QMessageBox.Ok)
            return 0

    # zero stage
    def center_stage(self):
        """
        Moves the stage to its centre position.
        """
        self.move(ctypes.c_double(self._RANGE/2), 1, self.handle)  # zero x axis
        self.move(ctypes.c_double(self._RANGE/2), 2, self.handle)  # zero y axis

    # get stage position of specified axis
    def read_stage(self, axis):
        """
        Get position of the stage.

        :param int Axis for which to return position.
        :return double Position of specified axis.
        """
        return float(self.getPosition(axis, self.handle))
