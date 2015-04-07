__author__ = 'df-setup-basement'

import numpy as np
import math


class HologramGeneration:
    def __init__(self):
        """
        initialise
        :return:
        """
        print ("Initialise Hologram generation. ")

    def create_delta_2(self, angle):
        """
        Create phase modulation matrix for SLM 2.
        :param angle: Matrix containing requested angles.
        :return: delta 2: phase modulation matrix.
        """
        delta_2 = np.zeros((np.size(angle, 0), np.size(angle, 1)), dtype=np.uint16)
        for i in range(np.size(angle, 0)):
            for j in range(np.size(angle, 1)):
                delta_2[i][j] = ((3 * math.pi - 2 * angle[i][j]) % (2 * math.pi))*(2**16-1)/(2*math.pi)
        return delta_2

    def create_azimuthal_polarization(self, dim, rotation):
        """
        Creates angle array with azimuthal polarizations.
        :param dim:
        :param rotation: rotation in degrees.
        :return:
        """
        theta_array = np.zeros((dim, dim))

        for i in range(np.size(theta_array, 0)):
            for j in range(np.size(theta_array, 1)):
                x = -dim / 2 + i
                y = -dim / 2 + j
                # perform roation
                th = math.pi*rotation/180.0
                x = np.cos(th)*x - np.sin(th)*y
                y = np.sin(th)*x + np.cos(th)*y

                rot = math.atan2(x, y) + math.pi/2
                # factor = (rot % (2*math.pi))
                theta_array[i][j] = (rot % (2 * math.pi))
        return theta_array


    def create_radial_polarization(self, dim, rotation):
        """
        Creates angle array with radial polarizations.
        :param dim:
        :param rotation: rotation in degrees.
        :return:
        """
        theta_array = np.zeros((dim, dim))
        for i in range(np.size(theta_array, 0)):
            for j in range(np.size(theta_array, 1)):
                x = -dim / 2 + i
                y = -dim / 2 + j

                # perform roation
                th = math.pi*rotation/180.0
                x = np.cos(th)*x - np.sin(th)*y
                y = np.sin(th)*x + np.cos(th)*y

                rot = math.atan2(x, y)
                theta_array[i][j] = (rot % (2 * math.pi))
        return theta_array

