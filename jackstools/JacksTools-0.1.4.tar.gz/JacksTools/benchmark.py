'''
suit of functions for general benchmarking of python functions
'''
import sys, os, multiprocessing, time, threading, re, math
import numpy as np
from matplotlib.pyplot import subplots, show
from JacksTools import transformations

#Constants

CPU_CORES = multiprocessing.cpu_count() #Number of cores
READ_RATE = 50 #Number of times per second that hardware state is read


##Hardware Locations:
CPU_INFO = '/proc/cpuinfo' #File location for the CPU
CPU_TEMP = '/sys/class/thermal/thermal_zone6/temp' #File location for the temperature

##Search Patterns
CPU_FREQ = 'cpu MHz		: (\d+\.\d+)' #Pattern to find CPU freq

#Flags

BENCH_TEMP = True #Record CPU temps
BENCH_FREQ = True #Record CPU freqs
BENCH_TIME = True #Record Run times

BENCH_PLOT = False #Plot Results


#fuctions

def readCPUfreqs():
	'''Return the freqencies of the CPU cores (MHz)'''
	with open(CPU_INFO,'rb') as info:
		freqs = re.findall(CPU_FREQ, info.read())
	return freqs

def readCPUtemps():
	'''return the temperature of the CPU (mC)'''
	with open(CPU_TEMP, 'rb') as temp:
		temp = temp.readline()	
	return temp


#classes

class Monitor(threading.Thread):
	'''Monitors the machines state while something runs'''

	def __init__(self):
		super(Monitor, self).__init__()

		self.data = {}
		self.files = {}
		if BENCH_TEMP:
			self.data['temp'] = []
			self.files['temp'] = open(CPU_TEMP,'rb')
		if BENCH_FREQ:
			self.data['freq'] = []
			self.files['freq'] = open(CPU_INFO,'rb')
		if BENCH_TIME:
			self.data['time'] = []

		self.stopRequest = threading.Event() #request to stop the thread

	def plotData(self):
	
		fig, ax = subplots(2,1)
		W = READ_RATE/2
		for i in xrange(CPU_CORES):
			y, x = transformations.smooth_([self.getFreqs()[:,i], self.getTimes()], N = W)
			x = x[W:-W]
			y = y[W:-W]
			ax[0].plot(x, y, color = 'k')
		y, x = transformations.smooth_([np.mean(self.getFreqs(), axis = 1), self.getTimes()], N = W)
		z, _ = transformations.smooth_([self.getTemps(), self.getTimes()], N = W)
		x = x[W:-W]
		y = y[W:-W]
		z = z[W:-W]
		ax[0].plot(x, y, color = 'r', lw = 1)
		ax[0].scatter(x, y, c = z/1000.0, edgecolor = 'none', marker = 'o')
		ax[0].set_xlim(min(x), max(x))

		ax[1].plot(x, z)
		show()

	def getTemps(self):
		'''return the temperatures as a numpy array'''
		return np.array(map(float, self.data['temp']))

	def getFreqs(self):
		'''return the frequencies as a numpy array'''
		return np.array([map(float, freqs) for freqs in self.data['freq']])

	def getTimes(self):
		'''return the times as a numpy array'''
		return np.array(self.data['time'])
		
	def readTemp(self):
		'''read the cpu temperatures'''
		self.files['temp'].flush()
		self.files['temp'].seek(0)
		self.data['temp'].append(self.files['temp'].readline().rstrip())

	def readFreq(self):
		'''read the CPU frequencies'''
		self.files['freq'].flush()
		self.files['freq'].seek(0)
		self.data['freq'].append(re.findall(CPU_FREQ, self.files['freq'].read()))

	def readTime(self):
		'''read the elapsed time since the first call to this function'''
		self.data['time'].append(time.clock())

	def readState(self):
		'''read the CPU state'''
		for f in self.data.iterkeys():
			if f == 'temp':
				self.readTemp()
			elif f == 'freq':
				self.readFreq()
			elif f == 'time':
				self.readTime()
			time.sleep(1.0/READ_RATE)

	def monitor(self):
		'''run the monitor'''	
		while not self.stopRequest.isSet():
			self.readState()	
		for value in self.files.values():
			value.close()
			value.close()

	def run(self):
		'''start the monitor'''
		time.clock()
		self.monitor()

	def join(self):
		'''stop the monitor'''
		self.stopRequest.set()
		super(Monitor, self).join()


class monitor_result:
	'''Picklable monitor object'''

	def __init__(self, parent):

		self.data = {}
		self.files = {}
		if BENCH_TEMP:
			self.data['temp'] = parent.data['temp']
		if BENCH_FREQ:
			self.data['freq'] = parent.data['freq']
		if BENCH_TIME:
			self.data['time'] = parent.data['time']

	def getTemps(self):
		'''return the temperatures as a numpy array'''
		return np.array(map(float, self.data['temp']))

	def getFreqs(self):
		'''return the frequencies as a numpy array'''
		return np.array([map(float, freqs) for freqs in self.data['freq']])

	def getTimes(self):
		'''return the times as a numpy array'''
		return np.array(self.data['time'])
	

#Benchmarking

def benchmark(func, *args, **kwargs):
	'''benchmark the machine state on a function'''
	monitor = Monitor()
	monitor.start()
	func(*args, **kwargs)
	monitor.join()
	return monitor_result(monitor)

def test():

	print readCPUfreqs()
	print readCPUtemps()
	benchmark(readCPUfreqs)

	#monitor = benchmark(test_func, np.random.randn(10000))

	#print monitor.getTemps()
	#print monitor.getFreqs()
	#print monitor.getTimes()
	#monitor.plotData()

if __name__ == '__main__':
	test()


