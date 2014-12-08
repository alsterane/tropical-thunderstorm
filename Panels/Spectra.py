__author__ = 'df-setup-basement'

from PyQt4 import uic, QtCore, QtGui
import pyqtgraph as pg
import numpy as np

class Spectra(pg.GraphicsWindow):

    def __init__(self):
        super(Spectra, self).__init__()
        self.setWindowTitle("Spectra Display")

        x2 = np.linspace(-100, 100, 100)
        data2 = np.sin(x2) / x2

        liveTraceFull = self.addPlot(title="Full Spectrum")
        liveTraceFull.plot(x2, data2)
        liveTraceFull.setLabel('bottom', 'wavelength (nm)')
        liveTraceFull.setLabel('left', 'counts', units=None)
        lr = pg.LinearRegionItem([-100, 100])
        lr.setZValue(-10)
        liveTraceFull.addItem(lr)

        # REGION OF INTEREST
        liveTraceROI = self.addPlot(title="ROI", row=0, col=1, colspan=2)
        liveTraceROI.plot(x2,data2)
        def update_plot():
            liveTraceROI.setXRange(*lr.getRegion(), padding=0)
        def update_region():
            lr.setRegion(liveTraceROI.getViewBox().viewRange()[0])
        lr.sigRegionChanged.connect(update_plot)
        liveTraceROI.sigXRangeChanged.connect(update_region)
        update_plot()

        self.nextRow()

        # HISTORY
        historyTrace = self.addPlot(title="History (ROI)")
        for i in range(1,5,1):
            historyTrace.plot(x2,data2+0.1*i)
        def update_plot():
            historyTrace.setXRange(*lr.getRegion(), padding=0)
        def update_region():
            lr.setRegion(liveTraceROI.getViewBox().viewRange()[0])
        lr.sigRegionChanged.connect(update_plot)
        historyTrace.sigXRangeChanged.connect(update_region)
        update_plot()

        # HISTOGRAMS of peak positions and intensities in ROI
        vals = np.hstack([np.random.normal(size=500), np.random.normal(size=260, loc=600)])
        y, x = np.histogram(vals, bins=np.linspace(-3, 8, 40))

        # HISTOGRAM PEAK POSITION
        histogramPosTrace = self.addPlot(title="Peak position")
        histogramPosTrace.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,100))
        def update_plot():
            y, x = np.histogram(vals, bins=np.linspace(lr.getRegion()[0], lr.getRegion()[1], 40))
            histogramPosTrace.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,100))
        def update_region():
            lr.setRegion(liveTraceROI.getViewBox().viewRange()[0])
        lr.sigRegionChanged.connect(update_plot)
        histogramPosTrace.sigXRangeChanged.connect(update_region)
        update_plot()

        # HISTOGRAM PEAK INTENSITY
        histogramIntTrace = self.addPlot(title="Peak intensity")
        histogramIntTrace.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,100))
        def update_plot():
            y, x = np.histogram(vals, bins=np.linspace(lr.getRegion()[0], lr.getRegion()[1], 40))
            histogramIntTrace.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,100))
        def update_region():
            lr.setRegion(liveTraceROI.getViewBox().viewRange()[0])
        lr.sigRegionChanged.connect(update_plot)
        histogramIntTrace.sigXRangeChanged.connect(update_region)
        update_plot()

