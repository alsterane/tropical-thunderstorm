__author__ = 'df-setup-basement'

from ctypes import *
import time
import traceback

# Device parameters
DAQmx_Val_ChanForAllLines = 1
DAQmx_Val_ChanPerLine = 0
DAQmx_Val_ContSamps = 10123
DAQmx_Val_Falling = 10171
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0
DAQmx_Val_High = 10192
DAQmx_Val_Hz = 10373
DAQmx_Val_Low = 10214
DAQmx_Val_Rising = 10280
DAQmx_Val_Volts = 10348
DAQmx_Val_RSE = 10083
DAQmx_Val_NRSE = 10078
DAQmx_Val_Diff = 10106
DAQmx_Val_PseudoDiff = 12529

TaskHandle = c_ulong

class NiDaqControl:

    def __init__(self):
        print("initialise")
        # load driver
        self.nidaqmx = windll.nicaiu

    def check_status(self, status):
        """
        Prints error code if status returns error message.
        :param status: Status
        """
        if status < 0:
            buf_size = 1000
            buf = create_string_buffer(buf_size)
            self.nidaqmx.DAQmxGetErrorString(c_long(status), buf, buf_size)
            print "nidaq error:", status, buf.value
            traceback.print_stack()

    def get_board_info(self):
        """
        Check attached NI devcies.
        :return: Array which lists NI devices that are attached to computer.
        """
        daq_boards = []
        devices_len = 100
        devices = create_string_buffer(devices_len)
        self.check_status(self.nidaqmx.DAQmxGetSysDevNames(devices, devices_len))
        devices_string = devices.value
        for dev in devices_string.split(", "):
            dev_data_len = 100
            dev_data = create_string_buffer(dev_data_len)
            c_dev = c_char_p(dev)
            self.check_status(self.nidaqmx.DAQmxGetDevProductType(c_dev, dev_data, dev_data_len))
            daq_boards.append([dev_data.value, dev[-1:]])
        return daq_boards

class NiDaqTask:
    """
    Initialises NI Task
    :param parent: parent national instrument control instance
    :param board: board name
    """
    def __init__(self, parent):
        self.parent = parent
        self.taskHandle = TaskHandle(0)
        self.parent.check_status(self.parent.nidaqmx.DAQmxCreateTask("", byref(self.taskHandle)))

    def clearTask(self):
        """
        Clears tasks from board.
        """
        self.parent.check_status(self.parent.nidaqmx.DAQmxClearTask(self.taskHandle))

    def startTask(self):
        """
        Starts task.
        """
        self.parent.check_status(self.parent.nidaqmx.DAQmxStartTask(self.taskHandle))

    def stopTask(self):
        """
        Stops task.
        """
        self.parent.check_status(self.parent.nidaqmx.DAQmxStopTask(self.taskHandle))


class VoltageOutput(NiDaqTask):

    def __init__(self, parent, board, channel, min_val = -10.0, max_val = 10.0):
        """
        Intialises voltage output instance.
        :param parent: parent NI control instance
        :param board: board name
        :param channel: output channel
        :param min_val: minimal voltage (optional, default -10 V)
        :param max_val: maximal voltage (optional, default +10 V)
        """
        NiDaqTask.__init__(self, parent)
        self.parent = parent
        self.channel = channel
        self.dev_and_channel = board + "/ao" + str(self.channel)
        self.parent.check_status(self.parent.nidaqmx.DAQmxCreateAOVoltageChan(self.taskHandle,
                                                     c_char_p(self.dev_and_channel),
                                                     "",
                                                     c_double(min_val),
                                                     c_double(max_val),
                                                     c_int(DAQmx_Val_Volts),
                                                     ""))

    def output_voltage(self, voltage):
        """
        Writes specified output voltage to previously specified port.
        :param voltage: Voltage
        """
        c_samples_written = c_long(0)
        c_voltage = c_double(voltage)
        self.parent.check_status(self.parent.nidaqmx.DAQmxWriteAnalogF64(self.taskHandle,
                                                c_long(1),
                                                c_long(1),
                                                c_double(10.0),
                                                c_long(DAQmx_Val_GroupByChannel),
                                                byref(c_voltage),
                                                byref(c_samples_written),
                                                None))
        assert c_samples_written.value == 1, "outputVoltage failed: " + str(c_samples_written.value) + " 1"

    # various helper functions

    def close_shutter(self):
        """
        Close Thorlabs SC 10 shutter (if  a shutter is connected to channel)
        """
        self.output_voltage(-5.0)

    def open_shutter(self):
        """
        Open Thorlabs SC 10 shutter (if  a shutter is connected to channel)
        """
        self.output_voltage(5.0)


if __name__ == "__main__":
    ni = NiDaqControl()
    print ni.get_board_info()

    vo = VoltageOutput(ni, 'cDAQ1Mod1', 0, -5.0, 5.0)
    vo.output_voltage(5.0)





