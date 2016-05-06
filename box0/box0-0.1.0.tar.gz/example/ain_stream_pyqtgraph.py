from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import box0

## derived from pyqtgraph demo "PlotWidget"

app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.setWindowTitle('AIN Demo')
mw.resize(800,800)

pw = pg.PlotWidget(name='AIN0')  ## giving the plots names allows us to link their axes together
mw.setCentralWidget(pw)
mw.show()

## Create an empty plot curve to be filled later, set its pen
p1 = pw.plot()
p1.setPen((200,200,100))

pw.setLabel('left', 'Value', units='V')
pw.setLabel('bottom', 'Time', units='s')
pw.setXRange(0, 1)
pw.setYRange(0, 3)

dev = box0.usb.open_supported()
ain0 = dev.ain(0)

sv = ain0.stream.search(96000, 12)
ain0.stream_prepare(sv)

class Poller(QtCore.QThread):
	feed = QtCore.pyqtSignal(np.ndarray, np.ndarray, name = 'feed')

	def __init__(self):
		QtCore.QThread.__init__(self)

	def start(self, mod, size):
		self.interruption_requested = False
		self.module = mod
		self.count = size
		QtCore.QThread.start(self)

	def stop(self):
		self.interruption_requested = True

	def run(self):
		global np
		while not self.interruption_requested:
			data = np.empty(self.count)
			self.module.stream_read(data)
			x = np.linspace(0.0, 1.0, sps)
			self.feed.emit(x, data)

ain0.stream_start()

def update(x, y):
	global p1
	p1.setData(y=y, x=x)

poller = Poller()
sps = sv.speed ## 1second
poller.feed.connect(update)
poller.start(ain0, sps)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

poller.stop()
poller.wait()

ain0.stream_stop()
ain0.close()
dev.close()
