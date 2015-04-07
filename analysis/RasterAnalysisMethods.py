__author__ = 'df-setup-basement'

import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
import panels.QuickPlot as quickplt
import pyqtgraph as pg

class RasterAnalysisMethods:
    """
    Contains list of methods to analyse raster scan.
    """

    def __init__(self):
        print("initialise")

        self.qp = None

    def peak_shift_vs_wavelength(self, wl_wave, array, start, stop, inc_pts, dim_px_x, dim_px_y):
        """
        :param wl_wave: wavelength data
        :param array: array with (x, y, lambda)
        :return:
        """
        center_x = []   # contains center x points of slices
        center_y = []   # contains center y points of slices
        wl_scale = []   # contains wl_scale of slices

        xdim = np.size(array, 0)
        ydim = np.size(array, 1)

        wl_wave = np.array(wl_wave)
        array = np.array(array)

        ind_start = self.find_nearest(wl_wave, start)
        ind_stop = self.find_nearest(wl_wave, stop)

        # iterate through slices in array and fit 2d gaussian to it
        for i in range(ind_start, ind_stop, inc_pts):
            # extract slice at particular wavelength
            sl = np.empty((xdim, ydim), dtype=np.float)
            for x in range(xdim):
                for y in range(ydim):
                    sl[x][y] = array[x][y][i]

            # fit 2d gaussian to it
            popt = self.fit_2d_gaussian(sl, dim_px_x, dim_px_y)
            center_x.append(popt[1]*dim_px_x)
            center_y.append(popt[2]*dim_px_y)
            wl_scale.append(wl_wave[i])

        # now create a plot
        self.qp = quickplt.QuickPlot('pixel', 'wavelength (nm)')
        self.qp.updatePlot(wl_scale, center_x, p=pg.mkPen(color=(255, 200, 200)))
        self.qp.updatePlot(wl_scale, center_y, p=pg.mkPen(color=(200, 200, 255)))

    def fit_2d_gaussian(self, sl, dim_px_x, dim_px_y):
        """
        Fits a two dimensional Gaussian to 2D intensity data.
        :param slice: 2D intensity data
        :param dim_px: dimension of one pixel in nm.
        :return:
        """
        x = np.linspace(0, np.size(sl, 0)-1, np.size(sl, 0))
        y = np.linspace(0, np.size(sl, 1)-1, np.size(sl, 1))
        x, y = np.meshgrid(x, y)
        amp_guess=np.amax(sl)
        sigma_guess_x = 500/dim_px_x
        sigma_guess_y = 500/dim_px_y
        # amplitude, x0, y0, sigma_x, sigma_y, theta, offset
        initial_guess = (amp_guess, np.size(sl, 0)/2, np.size(sl,1)/2, sigma_guess_x, sigma_guess_y, 0, 0.01)
        sl_linear = sl.ravel()
        print ("linear_shape" + str(np.shape(sl_linear)))
        popt, pcov = opt.curve_fit(self.gaussian_2d, (x, y), sl_linear, p0=initial_guess)
        return popt

    @staticmethod
    def gaussian_2d((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
        xo = float(xo)
        yo = float(yo)
        a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
        b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
        c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
        g = offset + amplitude*np.exp(-(a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))
        return g.ravel()

    def find_nearest(self, array, value):
        """
        :param array: array slice
        :param value: value
        :return: Index of entry whose value is closest to value.
        """
        idx = (np.abs(array-value)).argmin()
        return idx

def test_function():
    print "hi"
    rm = RasterAnalysisMethods()
    # Create x and y indices
    x = np.linspace(0, 200, 201)
    y = np.linspace(0, 200, 201)
    x, y = np.meshgrid(x, y)

    #create data
    data = rm.gaussian_2d((x, y), 3, 100, 100, 20, 40, 0, 10)

    # plot twoD_Gaussian data generated above
    plt.figure()
    plt.imshow(data.reshape(201, 201))
    plt.colorbar()

    initial_guess = (3,100,100,20,40,0,10)

    data_noisy = data + 0.2*np.random.normal(size=data.shape)
    print np.shape(data_noisy)

    popt, pcov = opt.curve_fit(rm.gaussian_2d, (x, y), data_noisy, p0=initial_guess)

    data_fitted = rm.gaussian_2d((x, y), *popt)

    fig, ax = plt.subplots(1, 1)
    ax.hold(True)
    ax.imshow(data_noisy.reshape(201, 201), cmap=plt.cm.jet, origin='bottom',
        extent=(x.min(), x.max(), y.min(), y.max()))
    ax.contour(x, y, data_fitted.reshape(201, 201), 8, colors='w')
    plt.show()
if __name__ == "__main__":
    test_function()