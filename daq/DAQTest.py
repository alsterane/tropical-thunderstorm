# coding= latin-1

from ctypes import byref
import PyDAQmx.DAQmxFunctions as daq
from PyDAQmx.DAQmxConstants import *

class ContinuousPulseTrainGeneration():
    """ Class to create a continuous pulse train on a counter
    
    Usage:  pulse = ContinuousTrainGeneration(period [s],
                duty_cycle (default = 0.5), counter (default = "dev1/ctr0"),
                reset = True/False)
            pulse.start()
            pulse.stop()
            pulse.clear()
    """
    def __init__(self, period=1., duty_cycle=0.5, counter="cDAQ1Mod1/ao0", reset=False):
        if reset:
            daq.DAQmxResetDevice(counter.split('/')[0])
        taskHandle = daq.TaskHandle(0)
        daq.DAQmxCreateTask("", byref(taskHandle))
        daq.DAQmxCreateCOPulseChanFreq(taskHandle, counter, "", 1000, -5, 0.0, 1/float(period),duty_cycle)
        daq.DAQmxCfgImplicitTiming(taskHandle, daq.DAQmx_Val_ContSamps, 1000)
        self.taskHandle = taskHandle



    def start(self):
        daq.DAQmxStartTask(self.taskHandle)
    def stop(self):
        daq.DAQmxStopTask(self.taskHandle)
    def clear(self):
        daq.DAQmxClearTask(self.taskHandle)


if __name__=="__main__":
    print ("Hello")




    g = ContinuousPulseTrainGeneration(1.,0.5, "cDAQ1Mod1/ao0", reset=True)
    g.start()

   