from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import box0
from scipy import signal

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

dev = box0.usb.open_supported()
ain0 = dev.ain(0)

ain0.static_prepare()

bs = 12
speed = 600000
ain0.bitsize.set(bs)
ain0.speed.set(speed)
byte_per_sample = (bs + 7) / 8
count = ain0.buffer.value / byte_per_sample

pw.setLabel('left', 'Value', units='V')
pw.setLabel('bottom', 'Time', units='s')
pw.setXRange(0, (1.0 * count) / speed)
pw.setYRange(0, 3)

def updateData():
	##filtering
	## http://stackoverflow.com/a/13740532
	#~ niqFreq = sv.speed / 2.0
	#~ cutoff = 100.0 # Hz
	#~ Wn = cutoff / niqFreq
	#~ order = 3
	#~ print("niqFreq:", niqFreq)
	#~ print("cutoff:", cutoff)
	#~ print("order:", order)
	#~ print("Wn:", Wn)
	#~ b, a = signal.butter(order, Wn, 'low')
	#~ y = signal.filtfilt(b, a, y)
	
	global speed, count
	y = np.empty(count)
	ain0.static_start(y)
	
	x = np.linspace(0.0, count, count) / speed
	p1.setData(y=y, x=x)

t = QtCore.QTimer()
t.timeout.connect(updateData)
t.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

t.stop()

ain0.close()
dev.close()
