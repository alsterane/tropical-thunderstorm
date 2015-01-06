__author__ = 'df-setup-basement'

import sys
from ctypes import *
import ctypes
import os

# control Andor spectrometer+camera through Andor DLL
class AndorControl():
    """
    * Readout modes
        * Full Vertical Binning (FVB)
        * Single Track
        * Multi Track
        * Random Track
        * Image
        * Cropped

    * Acquisition modes
        * Single scan
        * Accumulate
        * Kinetic series
        * Run till abort
        * Fast kinetics

            Single acquisition structure:
                FVB, single scan, then GetAcquiredData
    """

    # Error codes
    DRV_SUCCESS = 20002
    DRV_GENERAL_ERRORS = 20049

    def __init__(self):

        lib = ctypes.WinDLL('atmcd64d.dll')

        # return number of available cameras
        self.GetAvailableCameras = lib['GetAvailableCameras']

        # initialize functions
        self.Initialize = lib['Initialize']
        self.handle = 0
        self.GetDetector = lib['GetDetector']
        self.GetHardwareVersion = lib['GetHardwareVersion']
        self.GetNumberVSSpeeds = lib['GetNumberVSSpeeds']
        self.GetVSSpeed = lib['GetVSSpeed']
        self.GetSoftwareVersion = lib['GetSoftwareVersion']
        self.GetNumberHSSpeeds = lib['GetNumberHSSpeeds']
        self.GetHSSpeed = lib['GetHSSpeed']
        #
        self.SetReadMode = lib['SetReadMode']

        #
        self.SetAcquisitionMode = lib['SetAcquisitionMode']

        #
        self.SetExposureTime = lib['SetExposureTime']

        #
        self.GetAcquiredData = lib['GetAcquiredData']

        print "I'm here"
        self.initialise_andor()

    def initialise_andor(self):
        """
        :type int
        :param Integer
        :return:
        """

        if self.get_number_of_cameras() == 1:
            #workingPath = c_byte(0)
            tekst = c_char()
            working_path = os.path.abspath(tekst)
            print working_path

            status = self.Initialize(working_path)
            print status
        pcb = c_uint()
        decode = c_uint()
        dummy1 = c_uint()
        dummy2 = c_uint()
        firmware_version = c_uint()
        firmware_build = c_uint()

        #status = self.GetHardwareVersion(byref(pcb), byref(decode), byref(dummy1), byref(dummy2),
                                     # byref(firmware_version), byref(firmware_build))
        #if(status == self.DRV_SUCCESS):
        #     print pcb.value

    def get_number_of_cameras(self):
        # check for number of cameras
        num_cams = c_long(0)
        status = self.GetAvailableCameras(byref(num_cams))
        if num_cams.value < 1 and status == self.DRV_SUCCESS:
            raise ValueError("No cameras found.")
            return -1
        elif status == self.DRV_GENERAL_ERRORS:
            raise ValueError("Could not verify number of cameras.")
            return -1
        else:
            return num_cams.value


