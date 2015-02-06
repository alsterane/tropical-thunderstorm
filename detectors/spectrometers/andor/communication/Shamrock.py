from __future__ import division

from ctypes import *
import ctypes
from ThreadExecutor import *
import platform
import os

__author__ = 'df-setup-basement'

"""
Parts of this code were adapted from Eric Piel, Delmic
License: free software: GNU General Public License version 2 as published by the Free Software Foundation.
"""

class Shamrock():
    """
    Component representing the spectrograph part of the Andor Shamrock
    spectrometers.
    """
    def __init__(self):
        # DLL of spetrograph and camera need to be contained in same folder.
        # Camera intitialised first, then spectrograph

        # possible to pass a path of camera detector ini file.
        self._device = 0
        self._slit = None
        self._verbosity = True  # whether to output much info or not

        # load .dll library
        if platform.system() == "Windows":
            try:
                old_dir = os.getcwd()
                os.chdir(r"C:\\Program Files\\Andor SOLIS\\Drivers")
                self._dll = windll.LoadLibrary("ShamrockCIF.dll")
                os.chdir(old_dir)
            except:
                raise Exception("Failed to load Andor DLL. Please check specified path.")


        try:
            self.initialise()
        except:
            raise Exception("Failed to find Andor Shamrock.")
        try:
            nd = self.get_number_devices()
            print("Found " + str(nd) + " Spectrographs.")
            grating_choices = self.get_grating_choices()

            wl_range = (float("inf"), float("-inf"))
            for g in grating_choices:
                try:
                    wmin, wmax = self.get_wavelength_limits(1)
                except:
                    raise Exception("Failed to find wavelength limit for grating %d", g)
                    continue
                wl_range = min(wl_range[0], wmin), max(wl_range[1], wmax)

            # will take care of executing axis move asynchronously
            self._executor = CancellableThreadPoolExecutor(max_workers=1)   # one task at a time
        except Exception:
            self.close()
            raise

        # store currently active grating
        self._current_grating = self.get_grating()

    def initialise(self):
        """
        Initialise the currently selected device.
        """
        # Can take quite a lot of time due to the homing
        print("Initialising spectrograph.")
        err = self._dll.ShamrockInitialize()
        self.status("Initialisation", err)

    def close(self):
        err = self._dll.ShamrockClose()
        self.status("Closing spectrograph", err)

    def get_number_devices(self):
        """
        Get number of available Shamrocks.
        :return: int Number of Shamrocks.
        """
        no_devices = c_int()
        self._dll.ShamrockGetNumberDevices(byref(no_devices))
        return no_devices.value

    def get_serial_number(self):
        """
        Get the device serial number.
        :return: int Device serial number.
        """
        serial = create_string_buffer(64)
        self._dll.ShamrockGetSerialNumber(self._device, serial)
        return serial.value

    def ee_prom_get_optical_params(self):
        """
        Get optical parameters from Shamrock device.
        :return: (float, float, float) Focal length in m, angular deviation in degrees and focal tilt in degrees.
        """
        focal_length = c_float()
        angular_deviation = c_float()
        focal_tilt = c_float()
        self._dll.ShamrockEepromGetOpticalParams(
            self._device, byref(focal_length), byref(angular_deviation), byref(focal_tilt))
        return focal_length.value, angular_deviation.value, focal_tilt.value

    def set_grating(self, grating):
        """
        Set grating.
        :param grating: int grating to be set (1, 2, or 3).
        """
        assert 1 <= grating <= 3

        # Seems currently the SDK sometimes fail with SHAMROCK_COMMUNICATION_ERROR
        # as in SetWavelength()
        retry = 0
        while True:
            err = self._dll.ShamrockSetGrating(self._device, grating)
            if err != 20202 and retry <= 5:  # as long as no success and lower than 5 retries
                retry += 1
                print("Failed to set wavelength, will try again")
                time.sleep(0.1 * retry)
            else:
                break

    def get_grating(self):
        """
        Get currently selected grating.
        :return: int Number of currently active grating.
        """
        grating = c_int()
        self._dll.ShamrockGetGrating(self._device, byref(grating))
        return grating.value

    def get_number_gratings(self):
        """
        Get the number of installed gratings.
        :return: int Number of gratings present.
        """
        num_gratings = c_int()
        self._dll.ShamrockGetNumberGratings(self._device, byref(num_gratings))
        return num_gratings.value

    def wavelength_reset(self):
        """
        Resets the wavelength to 0 nm, i.e. move to zeroth order.
        """
        # Same as ShamrockGotoZeroOrder()
        self._dll.ShamrockWavelengthReset(self._device)

    def get_grating_info(self, grating):
        """
        Obtains information about specified grating.
        :param grating: int Grating number from which to obtain info.
        :return: (float, None/float, int, int) Number of lines/m, blaze wavelength in m or None if a mirror,
        home, i.e. beginning of grating in steps, offset, i.e. offset to the grating in steps.
        """
        assert 1 <= grating <= 3
        lines = c_float() # in l/mm
        blaze = create_string_buffer(64) # decimal of wavelength in nm
        home = c_int()
        offset = c_int()
        self._dll.ShamrockGetGratingInfo(self._device, grating,
                         byref(lines), blaze, byref(home), byref(offset))
        logging.debug("Grating is %f, %s, %d, %d", lines.value, blaze.value, home.value, offset.value)

        if blaze.value: # empty string if no blaze (= mirror)
            blaze = float(blaze.value) * 1e-9
        else:
            blaze = None
        return lines.value * 1e3, blaze, home.value, offset.value

    def set_wavelength(self, wavelength):
        """
        Sets the required wavelength.
        :param: wavelength in m.
        """
        assert 0 <= wavelength <= 5000
        # Note: When connected via the IC bus of the camera, it is not
        # possible to change the wavelength (or the grating) while the CCD
        # is acquiring. So this will fail with an exception, and that's
        # probably the best we can do (unless we want to synchronize with the
        # CCD and ask to temporarily stop the acquisition).

        # Currently the SDK sometimes fail with 20201: SHAMROCK_COMMUNICATION_ERROR
        # when changing wavelength by a few additional nm. It _seems_ that it
        # works anyway (but not sure).
        # It seems that retrying a couple of times just works

        retry = 0
        while True:
            # set in nm
            err = self._dll.ShamrockSetWavelength(self._device, c_float(wavelength))
            if err != 20202 and retry <= 5:  # as long as no success and lower than 5 retries
                # just try again
                retry += 1
                print("Failed to set wavelength, will try again")
                time.sleep(0.1)
            else:
                self.status("Wavelength change", err)
                break

    def get_wavelength(self):
        """
        Gets the current wavelength.
        return (0<=float): wavelength in nm.
        """
        wavelength = c_float()  # in nm
        self._dll.ShamrockGetWavelength(self._device, byref(wavelength))
        return wavelength.value

    def get_wavelength_limits(self, grating):
        """
        Returns wavelength limits of specified grating.
        :param grating: int Grating number
        :return: Min and max wavelength in nm.
        """
        assert 1 <= grating <= 3
        min, max = c_float(), c_float() # in nm
        self._dll.ShamrockGetWavelengthLimits(self._device, grating,
                                              byref(min), byref(max))
        return min.value, max.value

    def is_wavelength_present(self):
        """
        Finds if the turret motors are installed.
        :return: (boolean) Whether it is possible to change the wavelength
        """
        present = c_int()
        self._dll.ShamrockWavelengthIsPresent(self._device, byref(present))
        return present.value != 0

    def get_calibration(self, npixels):
        """
        npixels (0<int): number of pixels on the sensor. It's actually the
        length of the list that is being returned.
        return (list of floats of length npixels): wavelength in nm
        """
        assert(0 < npixels)
        # TODO: this is pretty slow, and could be optimised either by using a
        # numpy array or returning directly the C array. We could also just
        # allocate one array at the init, and reuse it.
        calibration_values = (c_float * npixels)()
        self._dll.ShamrockGetCalibration(self._device, calibration_values, npixels)
        return [v for v in calibration_values]

    def set_pixel_width(self, width):
        """
        Defines the size of each pixel (horizontally).
        Needed to get correct information from get_calibration()
        :param width: float Size of pixel in microns (um).
        """
        # set in um
        self._dll.ShamrockSetPixelWidth(self._device, c_float(width))

    def set_number_pixels(self, num_pixels):
        """
        Defines how many pixels (around the center) are used.
        Needed to get correct information from GetCalibration()
        npixels (int): number of pixels on the attached sensor
        """
        self._dll.ShamrockSetNumberPixels(self._device, num_pixels)

    def set_auto_slit_width(self, index, width):
        """
        Set width of specified slit.
        :param index: int Specifies slit (1-4). Input slit side = 1,
        input direct = 2, output side = 3, output direct = 4.
        :param width: float Width of slit in microns (um).
        """
        assert(1 <= index <= 4)
        width_um = c_float(width)
        self._dll.ShamrockSetAutoSlitWidth(self._device, index, width_um)

    def get_auto_slit_width(self, index):
        """
        Returns the specified Slit width.
        :param index: int Specifies slit (1-4). Input slit side = 1,
        input direct = 2, output side = 3, output direct = 4.
        :return: float Slit width in um.
        """
        assert (1 <= index <= 4)
        width_um = c_float()
        self._dll.ShamrockGetAutoSlitWidth(self._device, index, byref(width_um))
        return width_um.value

    def auto_slit_reset(self, index):
        """
        index (1<=int<=4): Slit number
        """
        assert(1 <= index <= 4)
        self._dll.ShamrockAutoSlitReset(self._device, index)

    def is_auto_slit_preset(self, index):
        """
        Finds if a specified slit is present.
        index (1<=int<=4): Slit number
        return (bool): True if slit is present
        """
        assert(1 <= index <= 4)
        present = c_int()
        self._dll.ShamrockAutoSlitIsPresent(self._device, index, byref(present))
        return present.value != 0

    # Helper functions
    def get_grating_choices(self):
        """
        Returns available grating choices.
        :return: (dict int -> string): grating number to description
        """
        num_gratings = self.get_number_gratings()
        g_choices = {}
        for g in range(1, num_gratings + 1):
            try:
                lines, blaze, home, offset = self.get_grating_info(g)
                if blaze is None:
                    g_choices[g] = "%.1f l/mm (mirror)" % (lines * 1e-3)
                else:
                    g_choices[g] = "%.1f l/mm (blaze: %g nm)" % (lines * 1e-3, blaze * 1e9)
            except Exception:
                g_choices[g] = "unknown"
        return g_choices

    # def get_pixel_to_wavelength(self, npixels=None):
    #     """
    #     Number of vertical pixels on the camera.
    #     npixels (None or int): number of pixels on the CCD (vertically)
    #     return (list of floats): pixel number -> wavelength in nm
    #     """
    #     # If wavelength is 0, report empty list to indicate it makes no sense
    #     if self.position.value["wavelength"] == 0:
    #         return []
    #     if npixels is None:
    #         ccd = self._ccd
    #         num_pixels = ccd.resolution.value[0]
    #     self.set_number_pixels(num_pixels)
    #     self.set_pixel_width(ccd._width * ccd._horizontal_binnnig)
    #     self.set_pixel_width(ccd.pixelSize.value[0] * ccd.binning.value[0])
    #     return self.get_calibration(num_pixels)

    def move_relative(self, shift):
        """
        Move the stage the defined values in m for each axis given.
        shift dict(string-> float): name of the axis and shift in m
        returns (Future): future that control the asynchronous move
        """
        self._checkMoveRel(shift)

        fs = []
        for axis in shift:
            if axis == "wavelength":
                # cannot convert it directly to an absolute move, because
                # several in a row must mean they accumulate. So we queue a
                # special task. That also means the range check is delayed until
                # the actual position is known.
                f = self._executor.submit(self.set_wavelength_relative, shift[axis])
                fs.append(f)
            elif axis == "slit":
                f = self._executor.submit(self.set_slit_relative, shift[axis])
                fs.append(f)
        # TODO: handle correctly when more than one future
        return fs[-1]


    def move_absolute(self, pos):
        """
        Move the stage the defined values in m for each axis given.
        pos dict(string-> float): name of the axis and new position in m
        returns (Future): future that control the asynchronous move
        """
        self._checkMoveAbs(pos)
        # If grating needs to be changed, change it first, then the wavelength
        fs = []
        if "grating" in pos:
            g = pos["grating"]
            wl = pos.get("wavelength")
            fs.append(self._executor.submit(self.set_grating_va, g, wl))
        elif "wavelength" in pos:
            wl = pos["wavelength"]
            fs.append(self._executor.submit(self.set_wavelength_absolute, wl))

        if "slit" in pos:
            width = pos["slit"]
            fs.append(self._executor.submit(self.set_slit_absolute, width))
        return fs[-1]

    def set_wavelength_relative(self, shift):
        """
        Change the wavelength by a value
        """
        pos = self.get_wavelength() + shift
        # it's only now that we can check the absolute position is wrong
        minp, maxp = self.axes["wavelength"].range
        if not minp <= pos <= maxp:
            raise ValueError("Position %f of axis '%s' not within range %f-%f" %
                             (pos, "wavelength", minp, maxp))

        # don't complain if the user asked for non reachable wl: he couldn't know
        minp, maxp = self.get_wavelength_limits(self.get_grating())
        pos = min(max(minp, pos), maxp)
        self.set_wavelength(pos)

    def set_wavelength_absolute(self, pos):
        """
        Change the wavelength to a value
        """
        # don't complain if the user asked for non reachable wl: he couldn't know
        minp, maxp = self.get_wavelength_limits(self.get_grating())
        pos = min(max(minp, pos), maxp)
        self.set_wavelength(pos)

    def set_grating_va(self, g, wl=None):
        """
        Setter for the grating VA.
        g (1<=int<=3): the new grating
        wl (None or float): wavelength to set afterwards. If None, will try to
          put the same wavelength as before the change of grating.
        returns the actual new grating
        Warning: synchronous until the grating is finished (up to 20s)
        """
        try:
            self.set_grating(g)
            # By default the Shamrock library keeps the same wavelength
            if wl is not None:
                self.set_wavelength(wl)
        except Exception:
            print("Failed to change grating to %d", g)

    def set_slit_relative(self, shift):
        """
        Change the slit width by a value
        """
        width = self.get_auto_slit_width(self._slit) + shift
        # it's only now that we can check the absolute position is wrong
        minp, maxp = self.axes["slit"].range
        if not minp <= width <= maxp:
            raise ValueError("Position %f of axis '%s' not within range %f-%f" %
                             (width, "slit", minp, maxp))

        self.set_auto_slit_width(self._slit, width)

    def set_slit_absolute(self, width):
        """
        Change the slit width to a value
        """
        self.set_auto_slit_width(self._slit, width)

    def stop(self):
        """
        Stops the motion.
        Warning: Only not yet-executed moves can be cancelled, this hardware
        doesn't support stopping while a move is going on.
        """
        self._executor.cancel()

    def terminate(self):
        """
        Shutdown spectrograph.
        """
        if self._executor:
            self.stop()
            self._executor.shutdown()
            self._executor = None

        if self._device is not None:
            logging.debug("Shutting down the spectrograph")
            self.close()
            self._device = None

    def test_connection(self):
        """
        Check whether the connection to the spectrograph works.
        return (boolean): False if it detects any problem
        """
        try:
            if 0 <= self.get_wavelength() <= 10e-6:
                return True
        except Exception:
            print("Self test failed.")
        return False

    def _deref(p, typep):
        """
        p (byref object)
        typep (c_type): type of pointer
        Use .value to change the value of the object
        """
        # This is using internal ctypes attributes, that might change in later
        # versions. Ugly!
        # Another possibility would be to redefine byref by identity function:
        # byref= lambda x: x
        # and then dereferencing would be also identity function.
        return typep.from_address(addressof(p._obj))

    def _val(obj):
        """
        return the value contained in the object. Needed because ctype automatically
        converts the arguments to c_types if they are not already c_type
        obj (c_type or python object)
        """
        if isinstance(obj, ctypes._SimpleCData):
            return obj.value
        else:
            return obj

    def status(self, action, code):
        """
        Writes status updates to command line.

        :param action: String describing the executed action.
        :param code: Return code.
        """
        if code != 20002:
            print(action + "returned  with code %s " % (ERROR_CODE[code]))
        elif self._verbosity:
            print(action + "completed successfully %s " % (ERROR_CODE[code]))


ERROR_CODE = {
20202: "SHAMROCK_SUCCESS",
20201: "SHAMROCK_COMMUNICATION_ERROR",
20266: "SHAMROCK_P1INVALID",
20267: "SHAMROCK_P2INVALID",
20268: "SHAMROCK_P3INVALID",
20269: "SHAMROCK_P4INVALID",
20275: "SHAMROCK_NOT_INITIALIZED",
20292: "SHAMROCK_NOT_AVAILABLE",
}

# Other constants
# SHAMROCK_ACCESSORYMIN 1
# SHAMROCK_ACCESSORYMAX 2
# SHAMROCK_FILTERMIN 1
# SHAMROCK_FILTERMAX 6
# SHAMROCK_TURRETMIN 1
# SHAMROCK_TURRETMAX 3
# SHAMROCK_GRATINGMIN 1
SLITWIDTHMIN = 10
SLITWIDTHMAX = 2500
# SHAMROCK_I24SLITWIDTHMAX 24000
# SHAMROCK_SHUTTERMODEMIN 0
# SHAMROCK_SHUTTERMODEMAX 1
# SHAMROCK_DET_OFFSET_MIN -240000
# SHAMROCK_DET_OFFSET_MAX 240000
# SHAMROCK_GRAT_OFFSET_MIN -20000
# SHAMROCK_GRAT_OFFSET_MAX 20000

# SHAMROCK_SLIT_INDEX_MIN    1
# SHAMROCK_SLIT_INDEX_MAX    4

INPUT_SLIT_SIDE = 1
INPUT_SLIT_DIRECT = 2
OUTPUT_SLIT_SIDE = 3
OUTPUT_SLIT_DIRECT = 4

# SHAMROCK_FLIPPER_INDEX_MIN    1
# SHAMROCK_FLIPPER_INDEX_MAX    2
# SHAMROCK_PORTMIN 0
# SHAMROCK_PORTMAX 1

# SHAMROCK_INPUT_FLIPPER   1
# SHAMROCK_OUTPUT_FLIPPER  2
# SHAMROCK_DIRECT_PORT  0
# SHAMROCK_SIDE_PORT    1

# SHAMROCK_ERRORLENGTH 64

def test():
    sham = Shamrock()
    sham.close()

if __name__ == '__main__':
    test()