__author__ = 'df-setup-basement'

import numpy as np
import matplotlib.pyplot as plt
import cv2
import math

class SimplePhaseGrating():
    """
    Creates a simple phase grating

    Input width, height, xpos, ypos
    hand an np array with SLM size (512 x 512 px)?
    """
    def __init__(self):
        # specify default values
        self.period = 10

    @property
    def mmin(self):
        """
        :return:(int) Minimum modulation (trough)
        """
        return self._mmin

    @mmin.setter
    def mmin(self,value):
        """
        :param value: (int) Set minimum depth of modulation (trough).
        """
        self._mmin = value

    @property
    def mmax(self):
        """
        :return:(int) Maximum modulation (peak)
        """
        return self._mmax

    @mmax.setter
    def mmax(self, value):
        """
        :param value: (int) Set maximum depth of modulation.
        """
        self._mmax = value

    @property
    def period(self):
        """:return:Grating period in px."""
        return self._period

    @period.setter
    def period(self, value):
        """
        :param value: Set grating period in px.
        """
        self._period = value

    # parameters: period, rotation (blazing?), shape?, phase, modulation? (depth -> start, stop)
    def createTestArray(self, per):
        d1=512
        d2=512
        array = np.empty([d1, d2], dtype=np.uint16)
        #array = np.empty([d1, d2])
        phase = math.pi/4
        a=1
        b=1

        for x in range(0, d1):
            for y in range(0, d2):
                array[x, y] = (2**16/2-1)*np.sin((y/per)*math.pi + phase)+(2**16)/2-1
                #array[x, y] = (2**16/2-1)*np.sin((np.sqrt((a*x-256)**2+(b*y-256)**2)/per)*math.pi + phase)+(2**16)/2-1
        cv2.imwrite('./output/processed_rot_b.tiff', array)
        return array

    def create_blazed_grating(self, per):
        d1=512
        d2=512
        array = np.empty([d1, d2], dtype=np.uint16)
        i = 0
        for y in range(0, d1):
            for x in range(0, d2):
                if i == per:
                    i = 0
                    array[x, y] = (2**16-1)*i/per
                else:
                    i+=1
                    array[x, y] = (2**16-1)*i/per
                #array[x, y] = (2**16/2-1)*np.sin((np.sqrt((a*x-256)**2+(b*y-256)**2)/per)*math.pi + phase)+(2**16)/2-1
            i = 0
        return array

    def createOneDTestArray(self, per):
        d1 = 512
        d2 = 512
        array = np.empty([d1*d2], dtype=np.uint16)
        array2D = np.empty([d1, d2], dtype=np.uint16)
        phase = math.pi/4
        a=1.0
        b=1.0

        for x in range(0, d1):
            for y in range(0, d2):
                #array2D[x, y] = 0 #(8000)*np.sin((np.sqrt((a*x-256)**2+(b*y-256)**2)/per)*math.pi + phase)+57000
                #array[x*d2 + y] = (8000)*np.sin((np.sqrt((a*x-256)**2+(b*y-256)**2)/per)*math.pi + phase)+57000
                array2D[x, y] = (2**16/2-1)*np.sin((y/per)*math.pi + phase)+(2**16)/2-1
                #array[x*d2 + y] = (2**16/2-1)*np.sin((np.sqrt((a*x-256)**2+(b*y-256)**2)/per)*math.pi + phase)+(2**16)/2-1
                #array[x*d2 + y] = (2**16/2-1)*np.sin((x/per)*math.pi + phase)+(2**16)/2-1
        return array


# code to test the class above
def main():
    grating = SimplePhaseGrating()

    f = open("sequence.seq", "w") #opens file with name of "test.txt"
    for i in range(60):
        array = grating.create_blazed_grating(10-i/10.0)
        cv2.imwrite('./output/processed_blaze_' + str(i) + '.tiff', array)
        f.write('C:\Users\df-setup-basement\PycharmProjects\Equipment\equipment\modulators\holograms\output\processed_blaze_'
                + str(i) + '.tiff\n')
    f.close()
if  __name__ =='__main__':main()

