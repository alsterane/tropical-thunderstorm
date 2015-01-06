"""
Module to control Andor idus camera and Shamrock 303i spectrograph

This code is partially based on code from David Baddeley, Hamid Ohadi and Martijn Schaafsma
"""

# required modules
from ctypes import windll, c_int, c_char, byref, c_long, pointer, c_float, c_char_p, cdll
from PIL import Image
import sys
import time
import platform
import os


class AndorIdus():
    """
    Provides functions to control Andor Idus camera and spectrograph
    For extensive documentation and specs see Andor SDK manual
    """

    def __init__(self):
        """
        Loads and initialises driver
        :return:
        """

        # load .dll library
        if platform.system() == "Windows":
            dllname = "C:\\Program Files\\Andor SOLIS\\Drivers\\atmcd64d"
            self._dll = windll.LoadLibrary(dllname)

        # initialise the device
        char_buffer = c_char()
        error = self._dll.Initialize(byref(char_buffer))
        print error
        print "Initialisation resulted in: %s" % (ERROR_CODE[error])

        # get ccd width and height from detector
        cw = c_int()
        ch = c_int()
        self._dll.GetDetector(byref(cw), byref(ch))

        # Initiate parameters
        self._width        = cw.value
        self._height       = ch.value
        self._temperature  = 20.0
        self._set_T        = None
        self._gain         = 1
        self._gainRange    = None
        self._status       = ERROR_CODE[error]
        self._verbosity    = True
        self._preampgain   = None
        self._channel      = None
        self._outamp       = None
        self._hsspeed      = None
        self._vsspeed      = None
        self._serial       = None
        self._exposure     = 1
        self._accumulate   = None
        self._kinetic      = None
        self._bitDepths    = []
        self._preAmpGain   = []
        self._VSSpeeds     = []
        self._noGains      = None
        self._imageArray   = []
        self._noVSSpeeds   = None
        self._HSSpeeds     = []
        self._noADChannels = None
        self._noHSSpeeds   = None
        self._ReadMode     = None

    def __del__(self):
       error = self._dll.ShutDown()
       print "Shutting down, %s" % (ERROR_CODE[error])

# ---------------------------------------------------------------------------------------------------
# Camera properties
# ---------------------------------------------------------------------------------------------------
    def get_camera_serial_number(self):
        """
        Returns serial number of camera
        :return: int Serial number of camera
        """
        serial = c_int()
        error = self._dll.GetCameraSerialNumber(byref(serial))
        self._serial = serial.value
        print ("Return serial number, %s" % (ERROR_CODE[error]))
        return self._serial

    def get_number_hs_speeds(self):
        """
        get number of HS speeds
        :return: int number of HS speeds
        """
        num_HSSpeeds = c_int()
        error = self._dll.GetNumberHSSpeeds(self._channel, self._outamp,
                                            byref(num_HSSpeeds))
        self._noHSSpeeds = num_HSSpeeds.value
        return self._noHSSpeeds

    def get_number_vs_speeds(self):
        """
        get number of VS speeds
        :return: int number of VS speeds
        """
        num_VSSpeeds = c_int()
        error = self._dll.GetNumberVSSpeeds(byref(num_VSSpeeds))
        self._noVSSpeeds = num_VSSpeeds.value
        return self._noVSSpeeds

# ---------------------------------------------------------------------------------------------------
# Cooler and temperature settings
# ---------------------------------------------------------------------------------------------------
    def enable_cooling(self):
        """
        Switches cooler on
        :return: status
        """
        error = self._dll.CoolerON()
        self._Verbose(ERROR_CODE[error])

    def disable_cooling(self):
        """
        Switches cooler off
        :return:
        """
        error = self._dll.CoolerOFF()
        self._Verbose(ERROR_CODE[error])

    def set_cooler_mode(self, mode):
        """
        set the cooler mode
        :param mode: int cooler modus
        :return:
        """
        error = self._dll.SetCoolerMode(mode)

    def is_cooling_enabled(self):
        """
        returns whether cooler is on or off
        :return: int cooler status
        """
        iCoolerStatus = c_int()
        error = self._dll.IsCoolerOn(byref(iCoolerStatus))
        return iCoolerStatus.value

    @property
    def get_temperature(self):
        """
        reads out temperature of CCD
        :return: int temperature in degree Celcius
        """
        temp = c_int()
        error = self._dll.GetTemperature(byref(temp))
        self._temperature = temp.value
        print "Temperature is: %g [Set T: %g]" % (self._temperature, self._set_T)
        return ERROR_CODE[error]

    def set_temperature(self, temperature):
        """
        set temperature of camera
        :param temperature: int temperature in degree Celcius
        :return:
        """
        temp = c_int(temperature)
        error = self._dll.SetTemperature(temp)
        self._set_T = temperature

# ---------------------------------------------------------------------------------------------------
# Set acquisition parameters
# ---------------------------------------------------------------------------------------------------
    def set_accumulation_cycle_time(self, time_):
        """
        set accumulation cycle time
        :param time_: int time between two accumulations
        :return:
        """
        error = self._dll.SetAccumulationCycleTime(c_float(time_))

    def set_acquisition_mode(self, mode):
        """
        Set acquisition mode
        """
        error = self._dll.SetAcquisitionMode(mode)

    def set_AD_channel(self, index):
        """
        set the A-D channel for acquisition
        :param index: int AD channel
        :return:
        """
        error = self._dll.SetADChannel(index)
        self._channel = index

    def SetEMAdvanced(self, gainAdvanced):
        '''
        Enable/disable access to the advanced EM gain levels

        Input:
            gainAdvanced (int) : 1 or 0 for true or false

        Output:
            None
        '''
        error = self._dll.SetEMAdvanced(gainAdvanced)

    def SetEMCCDGainMode(self, gainMode):
        '''
        Set the gain mode

        Input:
            gainMode (int) : mode

        Output:
            None
        '''
        error = self._dll.SetEMCCDGainMode(gainMode)
        #self._Verbose(ERROR_CODE[error] )

    def set_exposure_time(self, time_):
        """
        Set the exposure time in seconds
        :param time_: float, exposure time in seconds
        :return:
        """
        error = self._dll.SetExposureTime(c_float(time_))

    def set_frame_transfer_mode(self, frameTransfer):
        """
        set frame transfer mode
        :param frameTransfer: int 1, 0, to enable, disable frame transfer mode
        :return:
        """
        error = self._dll.SetFrameTransferMode(frameTransfer)

    def set_image_rotate(self, iRotate):
        """
        image rotation
        :param iRotate: int 0, 1, 2 for no rotation, 90 deg cw, 90 deg ccw
        :return:
        """
        error = self._dll.SetImageRotate(iRotate)

    def set_kinetic_cycle_time(self, time_):
        '''
        Set the Kinetic cycle time in seconds

        Input:
            time_ (float) : The cycle time in seconds

        Output:
            None
        '''
        error = self._dll.SetKineticCycleTime(c_float(time_))
        #self._Verbose(ERROR_CODE[error] )

    def set_number_accumulate(self, number):
        '''
        Set the number of scans accumulated in memory,
        for kinetic and accumulate modes

        Input:
            number (int) : The number of accumulations

        Output:
            None
        '''
        error = self._dll.SetNumberAccumulations(number)
        #self._Verbose(ERROR_CODE[error] )

    def set_number_kinetics(self, numKin):
        '''
        Set the number of scans accumulated in memory for kinetic mode

        Input:
            number (int) : The number of accumulations

        Output:
            None
        '''
        error = self._dll.SetNumberKinetics(numKin)
        #self._Verbose(ERROR_CODE[error] )

    def set_output_amp(self, index):
        '''
        Specify which amplifier to use if EMCCD is enabled

        Input:
            index (int) : 0 for EMCCD, 1 for conventional

        Output:
            None
        '''
        error = self._dll.SetOutputAmplifier(index)
        #self._Verbose(ERROR_CODE[error] )
        self._outamp = index

    def set_read_mode(self, mode):
        """
        set read mode of camera
        :param mode: int 0, 1, 2, 3, 4 for
            full vertical binning, multi-track, random-track, single-track, image
        :return:
        """
        error = self._dll.SetReadMode(mode)
        self._ReadMode = mode

    def set_trigger_mode(self, mode):
        '''
        Set the trigger mode

        Input:
            mode (int) : 0 Internal
                         1 External
                         2 External Start (only in Fast Kinetics mode)

        Output:
            None
        '''
        error = self._dll.SetTriggerMode(mode)
        #self._Verbose(ERROR_CODE[error] )

    def set_hs_speed(self, index):
        """
        set HS speed to mode corresponding to the index
        :param index: index corresponding to speed mode
        :return:
        """
        error = self._dll.SetHSSpeed(index)
        self._hsspeed = index

    def set_vs_speed(self, index):
        """
        set VS speed to mode corresponding to the index
        :param index: index corresponding to speed mode
        :return:
        """
        error = self._dll.SetVSSpeed(index)
        self._vsspeed = index

# ---------------------------------------------------------------------------------------------------
# Get acquisition parameters
# ---------------------------------------------------------------------------------------------------
    def get_accumulation_progress(self):
        """
        returns progress of accummulation
        :return: int number of completed accumulations
        """
        acc = c_long()
        series = c_long()
        error = self._dll.GetAcquisitionProgress(byref(acc), byref(series))
        return acc.value

    def get_acquired_data(self, img_array):
       """
       returns acquired data
       :param img_array: img_array which stores data
       :return: array containing acquired data
       """
        # FIXME : Check how this works for FVB !!!
        if self._ReadMode == 0:
            dim = self._width
        elif self._ReadMode == 4:
            dim = self._width * self._height
            
        print "Dim is %s" % dim
        c_img_array = c_int * dim
        c_img = c_img_array()
        error = self._dll.GetAcquiredData(pointer(c_img), dim)
        for i in range(len(c_img)):
            img_array.append(c_img[i])

        self._imageArray = img_array[:]
        return self._imageArray

    def get_bit_depth(self):
        """
        returns bit depth of available channels
        :return: int bit depths
        """
        bit_depth = c_int()
        self._bit_depths = []

        for i in range(self._noADChannels):
            self._dll.GetBitDepth(i, byref(bit_depth))
            self._bitDepths.append(bit_depth.value)
        return self._bitDepths

    def get_EM_gain_range(self):
        """
        returns gain range
        :return: int gain range
        """
        low = c_int()
        high = c_int()
        error = self._dll.GetEMGainRange(byref(low), byref(high))
        self._gainRange = (low.value, high.value)
        return self._gainRange

    def get_num_AD_channels(self):
        """
        returns number of AD channels
        :return: int number of AD channels
        """
        noADChannels = c_int()
        error = self._dll.GetNumberADChannels(byref(noADChannels))
        self._noADChannels = noADChannels.value
        return self._noADChannels

    def get_num_preamp_gains(self):
        """
        returns the number of Pre Amp Gains
        :return: int number of pre amp gains
        """
        noGains = c_int()
        error = self._dll.GetNumberPreAmpGains(byref(noGains))
        self._noGains = noGains.value
        return self._noGains

    def GetSeriesProgress(self):
        '''
        Returns the number of completed kenetic scans

        Input:
            None

        Output:
            (int) : The number of completed kinetic scans
        '''
        acc = c_long()
        series = c_long()
        error = self._dll.GetAcquisitionProgress(byref(acc), byref(series))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            return series.value
        else:
            return None

    def get_status(self):
        """
        returns status of camera
        :param: none
        :return: camera status (String)
            DRV_IDLE
            RV_TEMPCYCLE
            DRV_ACQUIRING
            DRV_TIME_NOT_MET
            DRV_KINETIC_TIME_NOT_MET
            DRV_ERROR_ACK
            DRV_ACQ_BUFFER
            DRV_SPOOLERROR
        """
        status = c_int()
        error = self._dll.GetStatus(byref(status))
        return self._status

###### Single Parameters Get/Set ######
    def GetEMCCDGain(self):
        """
        get gain
        :return:
        """
        gain = c_int()
        error = self._dll.GetEMCCDGain(byref(gain))
        self._gain = gain.value
        #self._Verbose(ERROR_CODE[error] )
        return self._gain

    def SetEMCCDGain(self, gain):
        '''
        Set the EMCCD Gain setting

        Input:
            gain (int) : EMCCD setting

        Output:
            None
        '''
        error = self._dll.SetEMCCDGain(gain)
        #self._Verbose(ERROR_CODE[error] )

    def GetHSSpeed(self):
        '''
        Returns the available HS speeds of the selected channel

        Input:
            None

        Output:
            (float[]) : The speeds of the selected channel
        '''
        HSSpeed = c_float()
        self._HSSpeeds = []
        for i in range(self._noHSSpeeds):
            self._dll.GetHSSpeed(self._channel, self._outamp, i, byref(HSSpeed))
            self._HSSpeeds.append(HSSpeed.value)
        return self._HSSpeeds

    def GetVSSpeed(self):
        '''
        Returns the available VS speeds of the selected channel

        Input:
            None

        Output:
            (float[]) : The speeds of the selected channel
        '''
        VSSpeed = c_float()
        self._VSSpeeds = []

        for i in range(self._noVSSpeeds):
            self._dll.GetVSSpeed(i, byref(VSSpeed))
            self._VSSpeeds.append(VSSpeed.value)
        return self._VSSpeeds

    def get_preamp_gain(self):
        """
        returns available pre amp gain
        :return: float preamp gain
        """
        gain = c_float()
        self._preAmpGain = []
        for i in range(self._noGains):
            self._dll.GetPreAmpGain(i, byref(gain))
            self._preAmpGain.append(gain.value)
        return self._preAmpGain

    def set_preamp_gain(self, index):
        """
        set pre amp gain to mode corresponding to index
        :param index: int index, corresponding to gain mode
        :return:
        """
        error = self._dll.SetPreAmpGain(index)
        self._preampgain = index


# ---------------------------------------------------------------------------------------------------
# Idus control functions (acquisition, etc.)
# ---------------------------------------------------------------------------------------------------
    def shutdown(self): # Careful with this one!!
        """
        shuts down camera
        :return:
        """
        error = self._dll.ShutDown()

    def abort_acquisition(self):
        """
        aborts current acquisition
        :return:
        """
        error = self._dll.AbortAcquisition()

    def start_acquisition(self):
        """
        starts acquisition
        :return:
        """
        error = self._dll.StartAcquisition()

    def set_single_image(self):
        """
        apply settings for single full image scan
        """
        self.set_read_mode(4)
        self.set_acquisition_mode(1)
        print "Width: %d Height: %d" % (self._width, self._height)
        self.set_image(1, 1, 1, self._width, 1, self._height)

    def set_single_FVB(self):
        """
        apply settings for single scan FVB (full vertical binning) acquisition
        """
        self.set_read_mode(0)
        self.set_acquisition_mode(1)

    def get_acquisition_timings(self):
        """
        Acquire all the relevant timings for acquisition,
        and store them in local memory
        :return:
        """
        exposure = c_float()
        accumulate = c_float()
        kinetic = c_float()
        error = self._dll.GetAcquisitionTimings(byref(exposure), byref(accumulate), byref(kinetic))
        self._exposure = exposure.value
        self._accumulate = accumulate.value
        self._kinetic = kinetic.value

# ---------------------------------------------------------------------------------------------------
# Misc functions
# ---------------------------------------------------------------------------------------------------
    def set_image(self, hbin, vbin, hstart, hend, vstart, vend):
        """
        specifiy binning and domain of image
        :param hbin: int horizontal binning
        :param vbin: int vertical binning
        :param hstart: horizontal starting point
        :param hend: horizontal end point
        :param vstart: vertical starting point
        :param vend: vertical end point
        :return:
        """
        error = self._dll.SetImage(hbin, vbin, hstart, hend, vstart, vend)

    def set_shutter(self, typ, mode, closingtime, openingtime):
        """
        set shutter configuration
        :param typ: int 0, 1: TTL low/high
        :param mode: int 0, 1, 2: auto, open, close
        :param closingtime: int ms it takes to close
        :param openingtime: int ms it takes to open
        :return:
        """
        error = self._dll.SetShutter(typ, mode, closingtime, openingtime)

    def set_shutter_ext(self, typ, mode, closingtime, openingtime, extmode):
        """
        conifgure shutter in external mode
        :param typ: int 0,1 : TTL low/high to open shutter
        :param mode: int 0,1,2 : auto, open, close
        :param closingtime: int ms shutter takes to close
        :param openingtime: int ms shutter takes to open
        :param extmode: int 0, 1, 2 : auto, open, close
        :return:
        """
        error = self._dll.SetShutterEx(typ, mode, closingtime, openingtime,
                                       extmode)

    def set_spool(self, active, method, path, framebuffersize):
        """
        set spooling
        :param active:
        :param method:
        :param path:
        :param framebuffersize:
        :return:
        """
        error = self._dll.SetSpool(active, method, c_char_p(path),
                                   framebuffersize)

    def save_as_bmp(self, path):
        """
        saves most recent acquired image as bmp
        :param path: string path
        :return:
        """
        im = Image.new("RGB", (self._height, self._width), "white")
        pix = im.load()
        for i in range(len(self._imageArray)):
            (row, col) = divmod(i, self._width)
            picvalue = int(round(self._imageArray[i]*255.0/65535))
            pix[row, col] = (picvalue, picvalue, picvalue)
        im.save(path,"BMP")

    def save_as_txt(self, path):
        """
        save most recent image as txt file in specified path
        :param path: string path where to save
        :return:
        """
        filename = open(path, 'w')

        for line in self._imageArray:
            filename.write("%g\n" % line)
        filename.close()

    def save_as_normalized_bmp(self, path):
        """
        save most recent image as bmp file in specified path, but with maximized contrast
        :param path: string path where to save
        :return:
        """
        im = Image.new("RGB", (self._height, self._width),"white")
        pix = im.load()
        max_int = max(self._imageArray)
        min_int = min(self._imageArray)
        for i in range(len(self._imageArray)):
            (row, col) = divmod(i, self._width)
            picvalue = int(round((self._imageArray[i]-min_int)*255.0/
                (max_int-min_int)))
            pix[row, col] = (picvalue, picvalue, picvalue)
        im.save(path, "BMP")


# -----------------------------------------------------------------------------------
# Control functions
# -----------------------------------------------------------------------------------
    def cool_down(self, temperature):
        """
        cool down camera to specified temperature
        :return:
        """
        self.SetCoolerMode(1)
        self.SetTemperature(temperature)
        self.enable_cooling()

        while self.GetTemperature() is not 'DRV_TEMP_STABILIZED':
            time.sleep(10)

    def setup_FVB(self, gain, exposure):
        """
        prepare for full vertical binning acquisition
        :return:
        """
        PreAmpGain = gain
        self.SetSingleFVB()
        self.SetTriggerMode(0)
        #self.SetShutter(1, 1, 0, 0)
        self.SetPreAmpGain(PreAmpGain)
        self.SetExposureTime(exposure)

    def capture_FVB(self):
        """
        capture spectra with full vertical binning
        :return:
        """
        i = 0
        while i < 4:
            i += 1
            #print self.GetTemperature()
            #print self._temperature
            print "Ready for Acquisition"
            self.StartAcquisition()

            # Check for status
            #while self.GetStatus() is not 'DRV_IDLE':
            print "Data not yet acquired, waiting 0.5s"
            print self.GetStatus()
            time.sleep(0.5)

            data = []
            self.GetAcquiredData(data)
            self.SaveAsTxt("%03g.txt" % i)
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# List of error codes
# -----------------------------------------------------------------------------------
ERROR_CODE = {
    20001: "DRV_ERROR_CODES",
    20002: "DRV_SUCCESS",
    20003: "DRV_VXNOTINSTALLED",
    20006: "DRV_ERROR_FILELOAD",
    20007: "DRV_ERROR_VXD_INIT",
    20010: "DRV_ERROR_PAGELOCK",
    20011: "DRV_ERROR_PAGE_UNLOCK",
    20013: "DRV_ERROR_ACK",
    20024: "DRV_NO_NEW_DATA",
    20026: "DRV_SPOOLERROR",
    20034: "DRV_TEMP_OFF",
    20035: "DRV_TEMP_NOT_STABILIZED",
    20036: "DRV_TEMP_STABILIZED",
    20037: "DRV_TEMP_NOT_REACHED",
    20038: "DRV_TEMP_OUT_RANGE",
    20039: "DRV_TEMP_NOT_SUPPORTED",
    20040: "DRV_TEMP_DRIFT",
    20050: "DRV_COF_NOTLOADED",
    20053: "DRV_FLEXERROR",
    20066: "DRV_P1INVALID",
    20067: "DRV_P2INVALID",
    20068: "DRV_P3INVALID",
    20069: "DRV_P4INVALID",
    20070: "DRV_INIERROR",
    20071: "DRV_COERROR",
    20072: "DRV_ACQUIRING",
    20073: "DRV_IDLE",
    20074: "DRV_TEMPCYCLE",
    20075: "DRV_NOT_INITIALIZED",
    20076: "DRV_P5INVALID",
    20077: "DRV_P6INVALID",
    20083: "P7_INVALID",
    20089: "DRV_USBERROR",
    20091: "DRV_NOT_SUPPORTED",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}
# -----------------------------------------------------------------------------------