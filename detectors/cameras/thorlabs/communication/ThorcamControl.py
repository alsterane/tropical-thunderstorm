__author__ = 'df-setup-basement'


import MMCorePy
from PyQt4 import QtCore
from scipy import fftpack
from dialogs.SaveImage import *
import time

class ThorcamControl:

    def __init__(self, video_stream, gradient_editor):
        self.video_stream = video_stream
        self.gradient_editor = gradient_editor
        self.mmc = MMCorePy.CMMCore()
        self.mmc.loadDevice('ThorCam', 'ThorlabsUSBCamera', 'ThorCam')
        self.mmc.initializeDevice('ThorCam')
        self.mmc.setCameraDevice('ThorCam')
        self.mmc.setProperty('ThorCam', 'PixelType', 'RGB32bit')
        self.mmc.setProperty('ThorCam', 'PixelClockMHz', '40')
        self.mmc.setProperty('ThorCam', 'Exposure', '50')
        self.mmc.setProperty('ThorCam', 'HardwareGain', '100')
        print "Description : " + str(self.mmc.getDeviceDescription('ThorCam'))
        print "Property names: " + str(self.mmc.getDevicePropertyNames('ThorCam'))

        # parameters
        self.is_PSD = False  # by default don't take FFT
        self.is_gray = True  # by default show as gray scale image and not RGB
        self.img = 0

    def binning(self, binning_value):
        self.mmc.setProperty('ThorCam', 'Binning', str(binning_value))

    def exposure(self, exp_value):
        print "adjusting exposure to " + str(exp_value)
        self.mmc.setProperty('ThorCam', 'Exposure', str(exp_value))

    def frames(self, fps_value):
        self.mmc.setProperty('ThorCam', 'FPS', str(fps_value))

    def gain(self, gain_value):
        self.mmc.setProperty('ThorCam', 'HardwareGain', str(gain_value))

    def pxclock(self, clock_value):
        self.mmc.setProperty('ThorCam', 'PixelClockMHz', str(clock_value))

    def pxtype(self, pxtype_value):
        self.mmc.setProperty('ThorCam', 'PixelType', str(pxtype_value))

    # the update occurs in a separate stream
    def stream(self):
        if self.mmc.getRemainingImageCount() > 0:
            tmp = self.mmc.popNextImage()
            tmp = tmp.view(dtype=np.uint8).reshape(tmp.shape[0], tmp.shape[1], 4)[...,2::-1]
            if self.is_PSD:  # calculate psd of gray scale image
                tmp = (tmp[:, :, 0] + tmp[:, :, 1] + tmp[:, :, 2])/3
                tmp = np.log10(fftpack.fftshift(fftpack.fft2(tmp)))
                tmp = np.abs(tmp)**2
                self.img = (255.0 / tmp.max() * (tmp - tmp.min())).astype(np.uint8)
                self.video_stream.setImage(self.img, lut=self.gradient_editor.getLookupTable(256), levels=(0, 255), autoDownsample=True)
            else:  # either plot image in gray or as RGB
                if self.is_gray:
                    tmp = (tmp[:, :, 0] + tmp[:, :, 1] + tmp[:, :, 2])/3
                    self.img = (255.0 / tmp.max() * (tmp - tmp.min())).astype(np.uint8)
                    self.video_stream.setImage(self.img, lut=self.gradient_editor.getLookupTable(256), levels=(0, 255), autoDownsample=True)
                else:
                    self.img = tmp.astype(np.uint8)
                    self.video_stream.setImage(self.img, lut=None, levels=(0, 255), autoDownsample=True)

    # start the constant acquisition
    def run(self):
        print "run viewtimer"
        global viewtimer
        viewtimer = QtCore.QTimer()
        viewtimer.timeout.connect(self.stream)
        viewtimer.start(0)
        self.mmc.startContinuousSequenceAcquisition(1)

    # stop the constant acquisition
    def pause(self):
        if viewtimer.isActive():
            self.mmc.stopSequenceAcquisition()
            viewtimer.stop()

    def snap(self):
        self.mmc.snapImage()
        tmp = self.mmc.getImage()
        tmp = tmp.view(dtype=np.uint8).reshape(tmp.shape[0], tmp.shape[1], 4)[...,2::-1]
        if self.is_PSD:
            tmp = (tmp[:, :, 0] + tmp[:, :, 1] + tmp[:, :, 2])/3
            tmp = np.log10(fftpack.fftshift(fftpack.fft2(tmp)))
            tmp = np.abs(tmp)**2
            self.img = (255.0 / tmp.max() * (tmp - tmp.min())).astype(np.uint8)
            self.video_stream.setImage(self.img, lut=self.gradient_editor.getLookupTable(256), levels=(0,255), autoDownsample=True)
        else:  # either plot image in gray or as RGB
                if self.is_gray:
                    tmp = (tmp[:, :, 0] + tmp[:, :, 1] + tmp[:, :, 2])/3
                    self.img = (255.0 / tmp.max() * (tmp - tmp.min())).astype(np.uint8)
                    self.video_stream.setImage(self.img, lut=self.gradient_editor.getLookupTable(256), levels=(0, 255), autoDownsample=True)
                else:
                    self.img = tmp.astype(np.uint8)
                    self.video_stream.setImage(self.img, lut=None, levels=(0, 255), autoDownsample=True)

    def grab_image(self, delay):
        """
        Grabs an image.
        :return: image array.
        """
        time.sleep(delay)
        self.mmc.snapImage()
        tmp = self.mmc.getImage()
        tmp = tmp.view(dtype=np.uint8).reshape(tmp.shape[0], tmp.shape[1], 4)[...,2::-1]
        tmp = tmp.astype(np.uint8)
        return tmp

    def store(self):
        SaveImage(self.img)

    def toggle_gray_rgb(self):
        if self.is_gray:
            self.is_gray = False
        else:
            self.is_gray = True

    def toggle_psd(self):
        if self.is_PSD:
            self.is_PSD = False
        else:
            self.is_PSD = True





