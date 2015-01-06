__author__ = 'df-setup-basement'

from detectors.spectrometers.andor.communication.AndorIdus import *

andor = AndorIdus()
andor.Demo_FVBPrepare()
andor.Demo_FVBCapture()

#andor = iXonCamera()

#andor = AndorControl()

