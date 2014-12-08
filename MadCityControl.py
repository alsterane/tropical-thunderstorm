__author__ = 'Lars Herrmann'

import ctypes


# control MadCityLabs Piezo Stage through Madlib.dll
class MadCityControl:

    def __init__(self):
        lib = ctypes.WinDLL('Madlib.dll')
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

    # grabs the handle to the stage
    def initialise_stage(self):
        self.handle = self.initHandle()
        if self.handle == 0:
            print "Stage could not be found."
        else:
            self.printInfo(self.handle)
            print "Serial number of stage is: " + str(self.getSerial(self.handle))

    # releases the handle
    def disconnect_stage(self):
        self.disconnect(self.handle)

    # move stage to position along axis
    def move_stage(self, position, axis):
        self.move(ctypes.c_double(position), axis, self.handle)

    # zero stage
    def center_stage(self):
        self.move(ctypes.c_double(50.0), 1, self.handle)  # zero x axis
        self.move(ctypes.c_double(50.0), 2, self.handle)  # zero y axis

    # get stage position of specified axis
    def read_stage(self, axis):
        return self.getPosition(axis, self.handle)
