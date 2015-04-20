__author__ = 'df-setup-basement'

import numpy as np
import math

import matplotlib.pyplot as plt
import scipy.ndimage as ndimage


class HologramGeneration:
    def __init__(self):
        """
        initialise
        :return:
        """
        print ("Initialise Hologram generation. ")

    def create_delta_1_azi(self, x_offset, y_offset, dim, rot):
        phase = np.zeros((dim, dim))
        return self.create_delta_1(phase, self.create_azimuthal_polarization(x_offset, y_offset, dim, rot))

    def create_delta_1_rad(self, x_offset, y_offset, dim, rot):
        phase = np.zeros((dim, dim))
        return self.create_delta_1(phase, self.create_radial_polarization(x_offset, y_offset, dim, rot))

    def create_delta_2_azi(self, x_offset, y_offset, dim, rot):
        return self.create_delta_2(self.create_azimuthal_polarization(x_offset, y_offset, dim, rot))

    def create_delta_2_rad(self, x_offset, y_offset, dim, rot):
        return self.create_delta_2(self.create_radial_polarization(x_offset, y_offset, dim, rot))

    def create_delta_2(self, angle):
        """
        Create phase modulation matrix for SLM 2.
        :param angle: Matrix containing requested angles.
        :return: delta 2: phase modulation matrix.
        """
        return ((3*np.pi - 2*angle) % (2 * np.pi))*(2**16-1)/(2*np.pi)

    def create_delta_1(self, phase, angle):
        """
        Creates phase modulation matrix for SLM 1.
        :param phase: requested phase.
        :param angle: requested angle.
        :return: delta 1: phase modulation matrix.
        """
        return ((phase + angle - 3*np.pi / 2) % (2*np.pi))*((2**16-1)/(2*np.pi))

    def create_azimuthal_polarization(self, x_offset, y_offset,  dim, rot):
        """
        Creates angle array with azimuthal polarizations.
        :param dim: dimension of array to be returned
        :param rotation: rotation in degrees.
        :return:
        """
        th = math.pi*rot/180.0
        x = np.linspace(-dim/2+x_offset, dim/2+x_offset, dim)
        y = np.linspace(-dim/2+y_offset, dim/2+y_offset, dim)
        xv, yv = np.meshgrid(x, y)
        rot = np.arctan2(np.cos(th)*xv-np.sin(th)*yv, np.sin(th)*xv+ np.cos(th)*yv) + np.pi/2
        return rot % (2*np.pi)

    def create_radial_polarization(self, x_offset, y_offset, dim, rot):
        """
        Creates angle array with azimuthal polarizations.
        :param dim: dimension of array to be returned
        :param rotation: rotation in degrees.
        :return:
        """
        th = math.pi*rot/180.0
        x = np.linspace(-dim/2+x_offset, dim/2+x_offset, dim)
        y = np.linspace(-dim/2+y_offset, dim/2+y_offset, dim)
        xv, yv = np.meshgrid(x, y)
        rot = np.arctan2(np.cos(th)*xv-np.sin(th)*yv, np.sin(th)*xv+ np.cos(th)*yv)
        return rot % (2*np.pi)


