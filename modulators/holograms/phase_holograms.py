__author__ = 'loh20'

import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import sys
import random
import cv2
import scipy.ndimage.interpolation as interp


def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    '''
    import matplotlib as mpl
    import numpy as np
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return cmap


c = mcolors.ColorConverter().to_rgb
#rvb = make_cmap([(1, 0, 0), (1, 1, 1), (0, 0, 1), (0, 0, 0), (1, 0, 0)], position=[0, .25, .5, .75, 1], bit=False)
rvb = make_cmap([(1, 1, 1), (.7, .4, 0), (0, 0, 0), (0, 0, 0.5), (1, 1, 1)], position=[0, .25, .5, .75, 1], bit=False)


def create_delta_1(phase, angle):
    """
    Creates phase modulation matrix for SLM 1.
    :param phase: requested phase.
    :param angle: requested angle.
    :return: delta 1: phase modulation matrix.
    """
    delta_1 = np.zeros((np.size(phase, 0), np.size(phase, 1)))
    for i in range(np.size(delta_1, 0)):
        for j in range(np.size(delta_1, 1)):
            delta_1[i][j] = ((phase[i][j] + angle[i][j] - 3 * math.pi / 2) % (2*math.pi))*((2**16-1)/(2*math.pi))
    return delta_1


def create_delta_2(angle):
    """
    Create phase modulation matrix for SLM 2.
    :param angle: Matrix containing requested angles.
    :return: delta 2: phase modulation matrix.
    """
    delta_2 = np.zeros((np.size(angle, 0), np.size(angle, 1)), dtype=np.uint16)
    for i in range(np.size(angle, 0)):
        for j in range(np.size(angle, 1)):
            delta_2[i][j] = ((3 * math.pi - 2 * angle[i][j]) % (2 * math.pi))*(2**16-1)/(2*math.pi)
    print np.amax(delta_2)
    return delta_2


def create_flat_phase(dim, phi_0):
    """
    returns flat phase matrix with specified value phi_0
    :param dim: Dimension of SLM.
    :param phi_0: specified flat phase.
    :return: flat phase matrix.
    """
    return np.ones((dim, dim)) * phi_0


def create_azimuthal_polarization(dim, rotation):
    """
    Creates angle array with azimuthal polarizations.
    :param dim:
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

def create_radial_polarization(dim):
    """
    Creates angle array with radial polarizations.
    :param dim:
    :return:
    """
    theta_array = np.zeros((dim, dim))

    for i in range(np.size(theta_array, 0)):
        for j in range(np.size(theta_array, 1)):
            x = -dim / 2 + i
            y = -dim / 2 + j

            rot = math.atan2(x, y)

            theta_array[i][j] = (rot % (2 * math.pi))
    return theta_array

def azi_to_rad_transformation(dim, frame, frame_tot):
    """
    Creates a certain frame in a continuous roation from radially to azimuthally polarized light.
    :param dim: dimension of SLM in pixels
    :param frame: current frame
    :param frame_tot: total number of frames
    :return: angle of current frame
    """
    theta_array = np.zeros((dim, dim))

    for i in range(np.size(theta_array, 0)):
        for j in range(np.size(theta_array, 1)):
            x = -dim / 2 + i
            y = -dim / 2 + j
            rot = math.atan2(x, y) + math.pi/2 * (float(frame)/float(frame_tot))
            theta_array[i][j] = (rot % (2 * math.pi))
    return theta_array

def create_azi_to_rad_sequence():
    """
    Creates hologram sequence of continuous rotation from azi to radially polarized light
    :return:
    """
    num_tot = 30
    for i in range(2*num_tot + 1):
        angle_arr = azi_to_rad_transformation(512, i, 30)
        phase_arr = create_flat_phase(512, 0)
        delta_1_arr = create_delta_1(phase_arr, angle_arr)
        delta_2_arr = create_delta_2(angle_arr)
        cv2.imwrite('frame' + str(i) +'.tiff', delta_2_arr)
        print("Frame " + str(i))

def create_random_linear_polarization(dim):
    theta_array = np.zeros((dim, dim))

    for i in range(np.size(theta_array, 0)):
        for j in range(np.size(theta_array, 1)):
            x = -dim / 2 + i
            y = -dim / 2 + j
            rot = random.uniform(0, 2*math.pi)
            theta_array[i][j] = (rot % (2 * math.pi))
    return theta_array



angle_arr = create_azimuthal_polarization(512, 45)
phase_arr = create_flat_phase(512, 0)
delta_1_arr = create_delta_1(phase_arr, angle_arr)
delta_2_arr = create_delta_2(angle_arr)
cv2.imwrite('radial_delta_2.tiff', delta_2_arr)

# sns.set(rc={'image.cmap': 'blue_red1'})
f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')

#delta_2_arr = interp.rotate(delta_2_arr, 45, reshape=False)

p1 = ax1.pcolormesh(angle_arr, cmap=rvb)
ax1.set_title('Angle')
ax1.set_ylabel('y (px)')
ax1.set_xlim([0, 512])
ax1.set_ylim([0, 512])
ax1.set_aspect('equal')
divider1 = make_axes_locatable(ax1)
cax1 = divider1.append_axes("right", size="5%", pad=0.15)
plt.colorbar(p1, cax=cax1)
cax1.set_ylabel('rad', rotation=270)
cax1.get_yaxis().labelpad = 15

p2 = ax2.pcolormesh(phase_arr, cmap=rvb)
ax2.set_title('Phase')
ax2.set_xlim([0, 512])
ax2.set_ylim([0, 512])
ax2.set_aspect('equal')
divider2 = make_axes_locatable(ax2)
cax2 = divider2.append_axes("right", size="5%", pad=0.15)
plt.colorbar(p2, cax=cax2)
cax2.set_ylabel('rad', rotation=270)
cax2.get_yaxis().labelpad = 15

p3 = ax3.pcolormesh(delta_1_arr, cmap=rvb)
ax3.set_title('Delta_1')
ax3.set_xlabel('x (px)')
ax3.set_ylabel('y (px)')
ax3.set_xlim([0, 512])
ax3.set_ylim([0, 512])
ax3.set_aspect('equal')
divider3 = make_axes_locatable(ax3)
cax3 = divider3.append_axes("right", size="5%", pad=0.15)
plt.colorbar(p3, cax=cax3)
cax3.set_ylabel('16-bit value', rotation=270)
cax3.get_yaxis().labelpad = 15

p4 = ax4.pcolormesh(delta_2_arr, cmap=rvb)
ax4.set_title('Delta_2')
ax4.set_xlabel('x (px)')
ax4.set_aspect('equal')
ax4.set_xlim([0, 512])
ax4.set_ylim([0, 512])
divider4 = make_axes_locatable(ax4)
cax4 = divider4.append_axes("right", size="5%", pad=0.15)
plt.colorbar(p4, cax=cax4)
cax4.set_ylabel('16-bit value', rotation=270)
cax4.get_yaxis().labelpad = 15




# cb = ax1.colorbar()
# cb.set_ticks((0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi))
# cb.ax1.set_yticklabels(('0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'))
#plt.tight_layout()
plt.savefig('test.png', dpi=300, facecolor='white', bbox_inches='tight', transparent="True", pad_inches=0)
plt.show()


