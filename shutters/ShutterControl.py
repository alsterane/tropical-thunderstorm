__author__ = 'df-setup-basement'


import time
import MMCorePy
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)


from PyQt4 import QtCore


class ShutterControl:
    def __init__(self):
        self.mmc = MMCorePy.CMMCore()
        self.mmc.loadDevice('Shutter', 'ThorlabsSC10', 'SC10')
        self.mmc.initializeAllDevices()
        print "Description : " + str(self.mmc.getDeviceDescription('SC10'))
        print "Property names: " + str(self.mmc.getDevicePropertyNames('SC10'))

def test_run():
    sht = ShutterControl()

if __name__ == "__main__":
   test_run()