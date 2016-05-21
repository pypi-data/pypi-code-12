import math
import numpy as np
import pylab
import scipy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import figure
import os
import pickle
import getpass
import mechanize
import pandas as pd

from tqdm import tqdm

weknowphysics = 0

try:
    import rowingphysics
    weknowphysics = 1
except ImportError:
    weknowphysics = 0

import time
import datetime

import dateutil
import writetcx

from dateutil import parser

from lxml import objectify
from math import sin,cos,atan2,sqrt
from numpy import isnan,isinf
from matplotlib.pyplot import grid
from pandas import Series, DataFrame
try:
    from Tkinter import Tk
    tkavail = 1
except ImportError:
    tkavail = 0
    
from matplotlib.ticker import MultipleLocator,FuncFormatter,NullFormatter
from sys import platform as _platform

__version__ = "0.80.5"

namespace = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'

# we're going to plot SI units - convert pound force to Newton
lbstoN = 4.44822


def main():
    return "Executing rowingdata version %s." % __version__


def spm_toarray(l):
    o = np.zeros(len(l))
    for i in range(len(l)):
	o[i] = l[i]

    return o

def tailwind(bearing,vwind,winddir):
    """ Calculates head-on head/tailwind in direction of rowing

    positive numbers are tail wind

    """

    b = math.radians(bearing)
    w = math.radians(winddir)

    vtail = -vwind*cos(w-b)
    
    return vtail

def copytocb(s):
    	""" Copy to clipboard for pasting into blog

	Doesn't work on Mac OS X
	"""
	if (_platform == 'win32'):
	    r = Tk()
	    r.withdraw()
	    r.clipboard_clear()
	    r.clipboard_append(s)
	    r.destroy
	    print "Summary copied to clipboard"

	else:
	    res = "Your platform {pl} is not supported".format(
		pl = _platform
		)
	    print res

def phys_getpower(velo,rower,rigging,bearing,vwind,winddirection):
    power = 0
    tw = tailwind(bearing,vwind,winddirection)
    if (weknowphysics==1):
	res = rowingphysics.constantvelofast(velo,rower,rigging,Fmax=600,
					     windv=tw)
	force = res[0]
	power = res[3]
	ratio = res[2]
	res2 = rowingphysics.constantwattfast(power,rower,rigging,Fmax=600,windv=0)
	vnowind = res2[1]
	pnowind = 500./res2[1]
	result = [power,ratio,force,pnowind]
	
    else:
	result = [0,0,0,0]

    return result

	    
def write_obj(obj,filename):
    """ Save an object (e.g. your rower) to a file
    """
    pickle.dump(obj,open(filename,"wb"))

def read_obj(filename):
    """ Read an object (e.g. your rower, including passwords) from a file
        Usage: john = rowingdata.read_obj("john.txt")
    """
    res = pickle.load(open(filename))
    return res

def getrigging(fileName="my1x.txt"):
    """ Read a rigging object
    """

    try:
	rg = pickle.load(open(fileName))
    except (IOError,ImportError,ValueError):
	if __name__ == '__main__':
	    print "Getrigging: File doesn't exist or is not valid. Creating new"
	    print fileName
	if (weknowphysics == 1):
	    rg = rowingphysics.rigging()
	else:
	    rg = 0

    return rg

def getrower(fileName="defaultrower.txt"):
    """ Read a rower object

    """

    try:
	r = pickle.load(open(fileName))
    except (IOError,ImportError):
	if __name__ == '__main__':
	    print "Getrower: Default rower file doesn't exist. Create new rower"
	r = rower()

    return r


def getrowtype():
    rowtypes = dict([
	('Indoor Rower',['1']),
	('Indoor Rower with Slides',['2']),
	('Dynamic Indoor Rower',['3']),
	('SkiErg',['4']),
	('Paddle Adapter',['5']),
	('On-water',['6']),
	('On-snow',['7'])
	])
    
    return rowtypes

def ewmovingaverage(interval,window_size):
    # Experimental code using Exponential Weighted moving average

    intervaldf = DataFrame({'v':interval})
    idf_ewma1 = intervaldf.ewm(span=window_size)
    idf_ewma2 = intervaldf[::-1].ewm(span=window_size)

    i_ewma1 = idf_ewma1.mean().ix[:,'v']
    i_ewma2 = idf_ewma2.mean().ix[:,'v']

    interval2 = np.vstack((i_ewma1,i_ewma2[::-1]))
    interval2 = np.mean( interval2, axis=0) # average

    return interval2

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

def interval_string(nr,totaldist,totaltime,avgpace,avgspm,
		    avghr,maxhr,avgdps,
		    separator='|'):
    """ Used to create a nifty text string with the data for the interval
    """

    stri = "{nr:0>2.0f}{sep}{td:0>5.0f}{sep}{inttime:0>5}{sep}".format(
	nr = nr,
	sep = separator,
	td = totaldist,
	inttime = format_pace(totaltime)
	)

    stri += "{tpace:0>7}{sep}{tspm:0>4.1f}{sep}{thr:3.1f}".format(
	tpace=format_pace(avgpace),
	sep=separator,
	tspm=avgspm,
	thr = avghr
	)

    stri += "{sep}{tmaxhr:3.1f}{sep}{tdps:0>4.1f}".format(
	sep = separator,
	tmaxhr = maxhr,
	tdps = avgdps
	)


    stri += "\n"
    return stri

def summarystring(totaldist,totaltime,avgpace,avgspm,avghr,maxhr,avgdps,
		  readFile="",
		  separator="|"):
    """ Used to create a nifty string summarizing your entire row
    """

    stri1 = "Workout Summary - "+readFile+"\n"
    stri1 += "--{sep}Total{sep}-Total-{sep}--Avg--{sep}Avg-{sep}-Avg-{sep}-Max-{sep}-Avg\n".format(sep=separator)
    stri1 += "--{sep}Dist-{sep}-Time--{sep}-Pace--{sep}SPM-{sep}-HR--{sep}-HR--{sep}-DPS\n".format(sep=separator)

    pacestring = format_pace(avgpace)


    #    stri1 += "--{sep}{dtot:0>5.0f}{sep}{tottime:7.1f}{sep}".format(
    stri1 += "--{sep}{dtot:0>5.0f}{sep}".format(
	sep = separator,
	dtot = totaldist,
	#tottime = format_time(totaltime),
	# pacestring = pacestring
	)

    stri1 += format_time(totaltime)+separator+pacestring
	

    stri1 += "{sep}{avgsr:2.1f}{sep}{avghr:3.1f}{sep}".format(
	avgsr = avgspm,
	sep = separator,
	avghr = avghr
	)

    stri1 += "{maxhr:3.1f}{sep}{avgdps:0>4.1f}\n".format(
	sep = separator,
	maxhr = maxhr,
	avgdps = avgdps
	)

    return stri1

def geo_distance(lat1,lon1,lat2,lon2):
    """ Approximate distance and bearing between two points
    defined by lat1,lon1 and lat2,lon2
    This is a slight underestimate but is close enough for our purposes,
    We're never moving more than 10 meters between trackpoints

    Bearing calculation fails if one of the points is a pole. 
    
    """
    
    # radius of earth in km
    R = 6373.0

    # pi
    pi = math.pi

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    tc1 = atan2(sin(lon2-lon1)*cos(lat2),
		cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1))

    tc1 = tc1 % (2*pi)

    bearing = math.degrees(tc1)

    return [distance,bearing]

def format_pace_tick(x,pos=None):
	min=int(x/60)
	sec=int(x-min*60.)
	sec_str=str(sec).zfill(2)
	template='%d:%s'
	return template % (min,sec_str)

def format_pace(x,pos=None):
    if isinf(x) or isnan(x):
	x=0
	
    min=int(x/60)
    sec=(x-min*60.)

    str1 = "{min:0>2}:{sec:0>4.1f}".format(
	min = min,
	sec = sec
	)

    return str1

def format_time(x,pos=None):


    min = int(x/60.)
    sec = int(x-min*60)

    str1 = "{min:0>2}:{sec:0>4.1f}".format(
	min=min,
	sec=sec,
	)

    return str1

def y_axis_range(ydata,miny=0,padding=.1,ultimate=[-1e9,1e9]):

    # ydata must by a numpy array

    ymin = np.ma.masked_invalid(ydata).min()
    ymax = np.ma.masked_invalid(ydata).max()


    yrange = ymax-ymin
    yrangemin = ymin
    yrangemax = ymax



    if (yrange == 0):
	if ymin == 0:
	    yrangemin = -padding
	else:
	    yrangemin = ymin-ymin*padding
	if ymax == 0:
	    yrangemax = padding
	else:
	    yrangemax = ymax+ymax*padding
    else:
	yrangemin = ymin-padding*yrange
	yrangemax = ymax+padding*yrange

    if (yrangemin < ultimate[0]):
	yrangemin = ultimate[0]

    if (yrangemax > ultimate[1]):
	yrangemax = ultimate[1]


    
    return [yrangemin,yrangemax]
    

def format_dist_tick(x,pos=None):
	km = x/1000.
	template='%6.3f'
	return template % (km)

def format_time_tick(x,pos=None):
	hour=int(x/3600)
	min=int((x-hour*3600.)/60)
	min_str=str(min).zfill(2)
	template='%d:%s'
	return template % (hour,min_str)

class summarydata:
    """ This is used to create nice summary texts from CrewNerd's summary CSV

    Usage: sumd = rowingdata.summarydata("crewnerdsummary.CSV")

           sumd.allstats()

	   sumd.shortstats()

	   """
    
    def __init__(self, readFile):
	self.readFile = readFile
	sumdf = pd.read_csv(readFile)
	self.sumdf = sumdf

	# prepare Work Data
	# remove "Just Go"
	#s2 = self.sumdf[self.sumdf['Workout Name']<>'Just Go']
	s2 = self.sumdf
	s3 = s2[~s2['Interval Type'].str.contains("Rest")]
	self.workdata = s3

    def allstats(self,separator="|"):



	stri2 = "Workout Details\n"
	stri2 += "#-{sep}SDist{sep}-Split-{sep}-SPace-{sep}SPM-{sep}AvgHR{sep}MaxHR{sep}DPS-\n".format(
	    sep = separator
	    )

	avghr = self.workdata['Avg HR'].mean()
	avgsr = self.workdata['Avg SR'].mean()
	maxhr = self.workdata['Max HR'].mean()
	maxsr = self.workdata['Max SR'].mean()
	totaldistance = self.workdata['Distance (m)'].sum()
	avgspeed = self.workdata['Avg Speed (m/s)'].mean()
	totalstrokes = self.workdata['Strokes'].sum()
	avgpace = 500./avgspeed



	min=int(avgpace/60)
	sec=int(10*(avgpace-min*60.))/10.
	pacestring = str(min)+":"+str(sec)


	nr_rows = self.workdata.shape[0]

	tothour = 0
	totmin = 0
	totsec = 0

	
	for i in range(nr_rows):
	    inttime = self.workdata['Time'].iloc[i]
	    thr = self.workdata['Avg HR'].iloc[i]
	    td = self.workdata['Distance (m)'].iloc[i]
	    tpace = self.workdata['Avg Pace (/500m)'].iloc[i]
	    tspm = self.workdata['Avg SR'].iloc[i]
	    tmaxhr = self.workdata['Max HR'].iloc[i]
	    tstrokes = self.workdata['Strokes'].iloc[i]

	    tdps = td/(1.0*tstrokes)
				 
	    try:
		t = datetime.datetime.strptime(inttime, "%H:%M:%S.%f")
	    except ValueError:
		t = datetime.datetime.strptime(inttime, "%M:%S")

	    tothour = tothour+t.hour

	    totmin = totmin+t.minute
	    if (totmin >= 60):
		totmin = totmin-60
		tothour = tothour+1

	    totsec = totsec+t.second+0.1*int(t.microsecond/1.e5) # plus tenths
	    if (totsec >= 60):
		totsec = totsec - 60
		totmin = totmin+1


	    stri2 += "{nr:0>2}{sep}{td:0>5}{sep} {inttime:0>5} {sep}".format(
		nr = i+1,
		sep = separator,
		td = td,
		inttime = inttime
		)

	    stri2 += "{tpace:0>7}{sep}{tspm:0>4.1f}{sep}{thr:3.1f}".format(
		tpace=tpace,
		sep=separator,
		tspm=tspm,
		thr = thr
		)

	    stri2 += "{sep}{tmaxhr:3.1f}{sep}{tdps:0>4.1f}".format(
		sep = separator,
		tmaxhr = tmaxhr,
		tdps = tdps
		)


	    stri2 += "\n"

	
	tottime = "{totmin:0>2}:{totsec:0>2}".format(
	    totmin = totmin+60*tothour,
	    totsec = totsec)

	totaltime = tothour*3600+totmin*60+totsec
	
	avgdps = totaldistance/(1.0*totalstrokes)
	if isnan(avgdps):
	    avgdps = 0


	stri1 = summarystring(totaldistance,totaltime,avgpace,avgsr,
			     avghr,maxhr,avgdps,
			     readFile=self.readFile,
			     separator=separator)

	
	print stri1+stri2

	copytocb(stri1+stri2)

	return stri1+stri2

    def shortstats(self):
	avghr = self.workdata['Avg HR'].mean()
	avgsr = self.workdata['Avg SR'].mean()
	maxhr = self.workdata['Max HR'].mean()
	maxsr = self.workdata['Max SR'].mean()
	totaldistance = self.workdata['Distance (m)'].sum()
	avgspeed = self.workdata['Avg Speed (m/s)'].mean()
	avgpace = 500/avgspeed

	min=int(avgpace/60)
	sec=int(10*(avgpace-min*60.))/10.
	pacestring = str(min)+":"+str(sec)


	nr_rows = self.workdata.shape[0]

	totmin = 0
	totsec = 0

	
	for i in range(nr_rows):
	    inttime = self.workdata['Time'].iloc[i]
	    try:
		t = time.strptime(inttime, "%H:%M:%S")
	    except ValueError:
		t = time.strptime(inttime, "%M:%S")

	    totmin = totmin+t.tm_min
	    totsec = totsec+t.tm_sec
	    if (totsec > 60):
		totsec = totsec - 60
		totmin = totmin+1

	stri =  "=========WORK DATA=================\n"
	stri = stri+"Total Time     : "+str(totmin)+":"+str(totsec)+"\n"
	stri = stri+ "Total Distance : "+str(totaldistance)+" m\n"
	stri = stri+"Average Pace   : "+pacestring+"\n"
	stri = stri+"Average HR     : "+str(int(avghr))+" Beats/min\n"
	stri = stri+"Average SPM    : "+str(int(10*avgsr)/10.)+" /min\n"
	stri = stri+"Max HR         : "+str(int(maxhr))+" Beats/min\n"
	stri = stri+"Max SPM        : "+str(int(10*maxsr)/10.)+" /min\n"
	stri = stri+"==================================="

	copytocb(stri)

	print stri
	

# Remark. I should write a generic CSV parser which takes a mapping to
# painsled column labels as input. Then rewrite the ErgData, RowPro, SpeedCoach
# parsers to use the generic CSV parser. 

class RowProParser:
    """ Parser for reading CSV files created by RowPro

    Use: data = rowingdata.RowProParser("RPdata.csv")

         data.write_csv("RPdata_out.csv")

	 """
    
    def __init__(self,RPfile="RPtest.csv",skiprows=14,skipfooter=24,
		 row_date=time.strftime("%c")):
	
	self.RP_df = pd.read_csv(RPfile,skiprows=skiprows,
				 skipfooter=skipfooter,
				 engine='python')
	self.row_date = row_date

    def write_csv(self,writeFile="example.csv"):
	""" Exports RowPro data to the CSV format that I use in rowingdata
	"""

	# Time,Distance,Pace,Watts,Cals,SPM,HR,DutyCycle,Rowfile_Id


	dist2 = self.RP_df['Distance']
	spm = self.RP_df['SPM']
	pace = self.RP_df['Pace']*500.0
	power = self.RP_df['Watts']

	seconds = self.RP_df['Time']/1000.

	time_incr = seconds.diff()
	time_incr[time_incr<0] = 0
	seconds2 = pd.Series(np.cumsum(time_incr)+seconds[0])
	seconds3 = seconds2.interpolate()
	seconds3[0] = seconds[0]

	# create unixtime using date
	dateobj = parser.parse(self.row_date)
	unixtimes = seconds3+time.mktime(dateobj.timetuple())


	hr = self.RP_df['HR']
	nr_rows = len(spm)

	# Create data frame with all necessary data to write to csv
	data = DataFrame({'TimeStamp (sec)':unixtimes,
			  ' Horizontal (meters)': dist2,
			  ' Cadence (stokes/min)':spm,
			  ' HRCur (bpm)':hr,
			  ' Stroke500mPace (sec/500m)':pace,
			  ' Power (watts)':power,
			  ' DriveLength (meters)':np.zeros(nr_rows),
			  ' StrokeDistance (meters)':np.zeros(nr_rows),
			  ' DriveTime (ms)':np.zeros(nr_rows),
			  ' StrokeRecoveryTime (ms)':np.zeros(nr_rows),
			  ' AverageDriveForce (lbs)':np.zeros(nr_rows),
			  ' PeakDriveForce (lbs)':np.zeros(nr_rows),
			  ' ElapsedTime (sec)':seconds3,
			  ' lapIdx':np.zeros(nr_rows)
			  })
	
#	data.sort(['TimeStamp (sec)'],ascending=True)
	data.sort_values(by='TimeStamp (sec)',ascending=True)

	return data.to_csv(writeFile,index_label='index')
	
	

class painsledDesktopParser:
    """ Parser for reading CSV files created by Painsled (desktop version)

    Use: data = rowingdata.painsledDesktopParser("sled_data.csv")

         data.write_csv("sled_data_out.csv")

	 """
    
    def __init__(self, sled_file="sled_test.csv"):
	df = pd.read_csv(sled_file)
	# remove "00 waiting to row"
	self.sled_df = df[df[' stroke.endWorkoutState'] != ' "00 waiting to row"']



    def time_values(self):
	""" Converts painsled style time stamps to Unix time stamps	"""
	
	# time stamps (ISO)
	timestamps = self.sled_df.loc[:,' stroke.driveStartMs'].values
	
	# convert to unix style time stamp
	unixtimes = np.zeros(len(timestamps))

	# there may be a more elegant and faster way with arrays 
	for i in range(len(timestamps)):
	    tt = parser.parse(timestamps[i],fuzzy=True)
	    unixtimes[i] = time.mktime(tt.timetuple())

	return unixtimes


    def write_csv(self,writeFile="example.csv"):
	""" Exports Painsled (desktop) data to the CSV format that
	I use in rowingdata
	"""
	

	unixtimes = self.time_values()

	
	dist2 = self.sled_df[' stroke.startWorkoutMeter']
	spm = self.sled_df[' stroke.strokesPerMin']
	pace = self.sled_df[' stroke.paceSecPer1k']/2.0
	power = self.sled_df[' stroke.watts']
	ldrive = self.sled_df[' stroke.driveMeters']
	strokelength2 = self.sled_df[' stroke.strokeMeters']
	tdrive = self.sled_df[' stroke.driveMs']
	trecovery = self.sled_df[' stroke.slideMs']
	hr = self.sled_df[' stroke.hrBpm']
	intervalcount = self.sled_df[' stroke.intervalNumber']

	nr_rows = len(spm)

	# Create data frame with all necessary data to write to csv
	data = DataFrame({'TimeStamp (sec)':unixtimes,
			  ' Horizontal (meters)': dist2,
			  ' Cadence (stokes/min)':spm,
			  ' HRCur (bpm)':hr,
			  ' Stroke500mPace (sec/500m)':pace,
			  ' Power (watts)':power,
			  ' DriveLength (meters)':ldrive,
			  ' StrokeDistance (meters)':strokelength2,
			  ' DriveTime (ms)':tdrive,
			  ' StrokeRecoveryTime (ms)':trecovery,
			  ' AverageDriveForce (lbs)':np.zeros(nr_rows),
			  ' PeakDriveForce (lbs)':np.zeros(nr_rows),
			  ' lapIdx':intervalcount,
			  ' ElapsedTime (sec)':unixtimes-unixtimes[0]
			  })

#	data.sort(['TimeStamp (sec)'],ascending=True)
	data.sort_values(by='TimeStamp (sec)',ascending=True)
	

	return data.to_csv(writeFile,index_label='index')

class speedcoachParser:
    """ Parser for reading CSV files created by SpeedCoach

    Use: data = rowingdata.speedcoachParser("speedcoachdata.csv")

         data.write_csv("speedcoach_data_out.csv")

	 """
    
    def __init__(self, sc_file="sc_test.csv",row_date=time.strftime("%c")):
	df = pd.read_csv(sc_file)
	self.sc_df = df
	self.row_date = row_date



    def write_csv(self,writeFile="example.csv"):
	""" Exports Painsled (desktop) data to the CSV format that
	I use in rowingdata
	"""

	seconds = self.sc_df['Time(sec)']

	# create unixtime using date
	dateobj = parser.parse(self.row_date)
	unixtime = seconds+time.mktime(dateobj.timetuple())

	dist2 = self.sc_df['Distance(m)']
	spm = self.sc_df['Rate']
	pace = self.sc_df['Split(sec)']

	hr = self.sc_df['HR']


	nr_rows = len(spm)

	# Create data frame with all necessary data to write to csv
	data = DataFrame({'TimeStamp (sec)':unixtime,
			  ' Horizontal (meters)': dist2,
			  ' Cadence (stokes/min)':spm,
			  ' HRCur (bpm)':hr,
			  ' Stroke500mPace (sec/500m)':pace,
			  ' Power (watts)':np.zeros(nr_rows),
			  ' DriveLength (meters)':np.zeros(nr_rows),
			  ' StrokeDistance (meters)':np.zeros(nr_rows),
			  ' DriveTime (ms)':np.zeros(nr_rows),
			  ' StrokeRecoveryTime (ms)':np.zeros(nr_rows),
			  ' AverageDriveForce (lbs)':np.zeros(nr_rows),
			  ' PeakDriveForce (lbs)':np.zeros(nr_rows),
			  ' lapIdx':np.zeros(nr_rows),
			  ' ElapsedTime (sec)':seconds
			  })

#	data.sort(['TimeStamp (sec)'],ascending=True)
	data.sort_values(by='TimeStamp (sec)',ascending=True)
	

	return data.to_csv(writeFile,index_label='index')

class ErgDataParser:
    """ Parser for reading CSV files created by ErgData/Concept2 logbook

    Use: data = rowingdata.ErgDataParser("ergdata.csv")

         data.write_csv("speedcoach_data_out.csv")

	 """
    
    def __init__(self, ed_file="ed_test.csv",row_date=time.strftime("%c")):
	df = pd.read_csv(ed_file)
	self.ed_df = df
	self.row_date = row_date



    def write_csv(self,writeFile="example.csv"):
	""" Exports  data to the CSV format that
	I use in rowingdata
	"""

	seconds = self.ed_df['Time (seconds)']

	# create unixtime using date
	dateobj = parser.parse(self.row_date)
	unixtime = seconds+time.mktime(dateobj.timetuple())

	dist2 = self.ed_df['Distance (meters)']
	spm = self.ed_df['Stroke Rate']
	pace = self.ed_df['Pace (seconds per 500m']

	hr = self.ed_df['Heart Rate']

	velocity = 500./pace
	power = 2.8*velocity**3


	nr_rows = len(spm)

	# Create data frame with all necessary data to write to csv
	data = DataFrame({'TimeStamp (sec)':unixtime,
			  ' Horizontal (meters)': dist2,
			  ' Cadence (stokes/min)':spm,
			  ' HRCur (bpm)':hr,
			  ' Stroke500mPace (sec/500m)':pace,
			  ' Power (watts)':power,
			  ' DriveLength (meters)':np.zeros(nr_rows),
			  ' StrokeDistance (meters)':np.zeros(nr_rows),
			  ' DriveTime (ms)':np.zeros(nr_rows),
			  ' StrokeRecoveryTime (ms)':np.zeros(nr_rows),
			  ' AverageDriveForce (lbs)':np.zeros(nr_rows),
			  ' PeakDriveForce (lbs)':np.zeros(nr_rows),
			  ' lapIdx':np.zeros(nr_rows),
			  ' ElapsedTime (sec)':seconds
			  })

#	data.sort(['TimeStamp (sec)'],ascending=True)
	data.sort_values(by=' ElapsedTime (sec)',ascending=True)
	

	return data.to_csv(writeFile,index_label='index')

	
class ErgStickParser:
    """ Parser for reading CSV files created by ErgStick

    Use: data = rowingdata.ErgStickParser("ergdata.csv")

         data.write_csv("speedcoach_data_out.csv")

	 """
    
    def __init__(self, ed_file="ed_test.csv",row_date=time.strftime("%c")):
	df = pd.read_csv(ed_file)
	self.es_df = df
	self.row_date = row_date



    def write_csv(self,writeFile="example.csv"):
	""" Exports  data to the CSV format that
	I use in rowingdata
	"""

	seconds = self.es_df['Total elapsed time (s)']
	time_incr = seconds.diff()
	time_incr[time_incr<0] = 0
	seconds2 = pd.Series(np.cumsum(time_incr)+seconds[0])
	seconds3 = seconds2.interpolate()
	seconds3[0] = seconds[0]
	


	# create unixtime using date
	dateobj = parser.parse(self.row_date)
	unixtime = seconds3+time.mktime(dateobj.timetuple())

	dist2 = self.es_df['Total distance (m)']
	spm = self.es_df['Stroke rate (/min)']
	pace = self.es_df['Current pace (/500m)']
	drivelength = self.es_df['Drive length (m)']
	strokedistance = self.es_df['Stroke distance (m)']
	drivetime = self.es_df['Drive time (s)']*1000.
	recoverytime = self.es_df['Stroke recovery time (s)']*1000.
	stroke_av_force = self.es_df['Ave. drive force (lbs)']
	stroke_peak_force = self.es_df['Peak drive force (lbs)']
	intervalcount = self.es_df['Interval count']

	hr = self.es_df['Current heart rate (bpm)']

	velocity = 500./pace
	power = 2.8*velocity**3


	nr_rows = len(spm)

	# Create data frame with all necessary data to write to csv
	data = DataFrame({'TimeStamp (sec)':unixtime,
			  ' Horizontal (meters)': dist2,
			  ' Cadence (stokes/min)':spm,
			  ' HRCur (bpm)':hr,
			  ' Stroke500mPace (sec/500m)':pace,
			  ' Power (watts)':power,
			  ' DriveLength (meters)':drivelength,
			  ' StrokeDistance (meters)':strokedistance,
			  ' DriveTime (ms)':drivetime,
			  ' StrokeRecoveryTime (ms)':recoverytime,
			  ' AverageDriveForce (lbs)':stroke_av_force,
			  ' PeakDriveForce (lbs)':stroke_peak_force,
			  ' lapIdx':intervalcount,
			  ' ElapsedTime (sec)':seconds3
			  })

#	data.sort(['TimeStamp (sec)'],ascending=True)
	data.sort_values(by='TimeStamp (sec)',ascending=True)
	

	return data.to_csv(writeFile,index_label='index')

class TCXParserTester:
    def __init__(self, tcx_file):
        tree = objectify.parse(tcx_file)
        self.root = tree.getroot()
        self.activity = self.root.Activities.Activity

	# need to select only trackpoints with Cadence, Distance, Time & HR data 
	self.selectionstring = '//ns:Trackpoint[descendant::ns:HeartRateBpm]'
	self.selectionstring +='[descendant::ns:Cadence]'
	self.selectionstring +='[descendant::ns:DistanceMeters]'
	self.selectionstring +='[descendant::ns:Time]'


	hr_values = self.root.xpath(self.selectionstring
			       +'//ns:HeartRateBpm/ns:Value',
			       namespaces={'ns': namespace})
        


        distance_values =  self.root.xpath(self.selectionstring
			       +'/ns:DistanceMeters',
			       namespaces={'ns': namespace})

	spm_values = self.root.xpath(self.selectionstring
			       +'/ns:Cadence',
			       namespaces={'ns': namespace})

    def getarray(self,str1,str2=''):
	s = self.selectionstring 
	s = s+'//ns:'+str1
	if (str2 != ''):
	    s = s+'/ns:'+str2

	y = self.root.xpath(s,namespaces={'ns': namespace})

	return y
	


class TCXParser:
    """ Parser for reading TCX files, e.g. from CrewNerd

    Use: data = rowingdata.TCXParser("crewnerd_data.tcx")

         data.write_csv("crewnerd_data_out.csv")

	 """

    
    def __init__(self, tcx_file):
        tree = objectify.parse(tcx_file)
        self.root = tree.getroot()
        self.activity = self.root.Activities.Activity

	# need to select only trackpoints with Cadence, Distance, Time & HR data 
	self.selectionstring = '//ns:Trackpoint[descendant::ns:HeartRateBpm]'
	self.selectionstring +='[descendant::ns:Cadence]'
	self.selectionstring +='[descendant::ns:DistanceMeters]'
	self.selectionstring +='[descendant::ns:Time]'


	hr_values = self.root.xpath(self.selectionstring
			       +'//ns:HeartRateBpm/ns:Value',
			       namespaces={'ns': namespace})
        


        distance_values =  self.root.xpath(self.selectionstring
			       +'/ns:DistanceMeters',
			       namespaces={'ns': namespace})

	spm_values = self.root.xpath(self.selectionstring
			       +'/ns:Cadence',
			       namespaces={'ns': namespace})


	# time stamps (ISO)
	timestamps = self.root.xpath(self.selectionstring
				    +'/ns:Time',
				    namespaces={'ns': namespace})
	
	lat_values = self.root.xpath(self.selectionstring
					  +'/ns:Position/ns:LatitudeDegrees',
					  namespaces={'ns':namespace})

	long_values = self.root.xpath(self.selectionstring
					   +'/ns:Position/ns:LongitudeDegrees',
					   namespaces={'ns':namespace})

	# and here are the trackpoints for "no stroke" 
	self.selectionstring2 = '//ns:Trackpoint[descendant::ns:HeartRateBpm]'
	self.selectionstring2 +='[descendant::ns:DistanceMeters]'
	self.selectionstring2 +='[descendant::ns:Time]'

	hr_values2 = self.root.xpath(self.selectionstring2
			       +'//ns:HeartRateBpm/ns:Value',
			       namespaces={'ns': namespace})
        


        distance_values2 =  self.root.xpath(self.selectionstring2
			       +'/ns:DistanceMeters',
			       namespaces={'ns': namespace})

	spm_values2 = np.zeros(len(distance_values2)).tolist()


	# time stamps (ISO)
	timestamps2 = self.root.xpath(self.selectionstring2
				    +'/ns:Time',
				    namespaces={'ns': namespace})
	
	lat_values2 = self.root.xpath(self.selectionstring2
					  +'/ns:Position/ns:LatitudeDegrees',
					  namespaces={'ns':namespace})

	long_values2 = self.root.xpath(self.selectionstring2
					   +'/ns:Position/ns:LongitudeDegrees',
					   namespaces={'ns':namespace})

	# merge the two datasets


	timestamps = timestamps+timestamps2
	
	self.hr_values = hr_values+hr_values2
	self.distance_values = distance_values+distance_values2

	self.spm_values = spm_values+spm_values2

	self.long_values = long_values+long_values2
	self.lat_values = lat_values+lat_values2

	# sort the two datasets
	data = pd.DataFrame({
	    't':timestamps,
	    'hr':self.hr_values,
	    'd':self.distance_values,
	    'spm':self.spm_values,
	    'long':self.long_values,
	    'lat':self.lat_values
	    })

	data = data.drop_duplicates(subset='t')
	data = data.sort_values(by='t',ascending = 1)

	timestamps = data.ix[:,'t'].values
	self.hr_values = data.ix[:,'hr'].values
	self.distance_values = data.ix[:,'d'].values
	self.spm_values = data.ix[:,'spm'].values
	self.long_values = data.ix[:,'long'].values
	self.lat_values = data.ix[:,'lat'].values

	# convert to unix style time stamp
	unixtimes = np.zeros(len(timestamps))

	# Activity ID timestamp (start)
	startdatetimeobj = parser.parse(str(self.root.Activities.Activity.Id),fuzzy=True)
	starttime = time.mktime(startdatetimeobj.timetuple())+startdatetimeobj.microsecond/1.e6

	self.activity_starttime = starttime

	# there may be a more elegant and faster way with arrays 
	for i in range(len(timestamps)):
	    s = str(timestamps[i])
	    tt = parser.parse(s)
	    unixtimes[i] = time.mktime(tt.timetuple())+tt.microsecond/1.e6

	self.time_values = unixtimes
	
	long = self.long_values
	lat = self.lat_values
	spm = self.spm_values

	nr_rows = len(lat)
	velo = np.zeros(nr_rows)
	dist2 = np.zeros(nr_rows)
	strokelength = np.zeros(nr_rows)
	
	for i in range(nr_rows-1):
	    res = geo_distance(lat[i],long[i],lat[i+1],long[i+1])
	    dl = 1000.*res[0]
	    dist2[i+1]=dist2[i]+dl
	    velo[i+1] = dl/(1.0*(unixtimes[i+1]-unixtimes[i]))
	    if (spm[i]<>0):
		strokelength[i] = dl*60/spm[i]
	    else:
		strokelength[i] = 0.


	self.strokelength = strokelength
	self.dist2 = dist2
	self.velo = velo



    def write_csv(self,writeFile='example.csv',window_size=20):
	""" Exports TCX data to the CSV format that
	I use in rowingdata
	"""

	# Time stamps 
	unixtimes = self.time_values


	# Distance Meters
	d = self.distance_values

	# Stroke Rate
	spm = self.spm_values
	
	# Heart Rate
	hr = self.hr_values

	long = self.long_values
	lat = self.lat_values

	nr_rows = len(spm)
	velo = np.zeros(nr_rows)
	dist2 = np.zeros(nr_rows)
	strokelength = np.zeros(nr_rows)

	velo = self.velo
	strokelength = self.strokelength
	dist2 = self.dist2

	velo2 = ewmovingaverage(velo,window_size)
	strokelength2 = ewmovingaverage(strokelength,window_size)
	
	pace = 500./velo2



	# Create data frame with all necessary data to write to csv
	data = DataFrame({'TimeStamp (sec)':unixtimes,
			  ' Horizontal (meters)': dist2,
			  ' Cadence (stokes/min)':spm,
			  ' HRCur (bpm)':hr,
			  ' longitude':long,
			  ' latitude':lat,
			  ' Stroke500mPace (sec/500m)':pace,
			  ' Power (watts)':np.zeros(nr_rows),
			  ' DriveLength (meters)':np.zeros(nr_rows),
			  ' StrokeDistance (meters)':strokelength2,
			  ' DriveTime (ms)':np.zeros(nr_rows),
			  ' StrokeRecoveryTime (ms)':np.zeros(nr_rows),
			  ' AverageDriveForce (lbs)':np.zeros(nr_rows),
			  ' PeakDriveForce (lbs)':np.zeros(nr_rows),
			  ' lapIdx':np.zeros(nr_rows),
			  ' ElapsedTime (sec)':unixtimes-self.activity_starttime
			  })

	
	self.data = data

	return data.to_csv(writeFile,index_label='index')
	

    def write_nogeo_csv(self,writeFile='example.csv',window_size=5):
	""" Exports TCX data without position data (indoor)
	to the CSV format that
	I use in rowingdata
	"""

	# Time stamps 
	unixtimes = self.time_values


	# Distance Meters
	d = self.distance_values

	# Stroke Rate
	spm = self.spm_values
	
	# Heart Rate
	hr = self.hr_values


	nr_rows = len(spm)
	velo = np.zeros(nr_rows)

	strokelength = np.zeros(nr_rows)

	for i in range(nr_rows-1):
	    dl = d[i+1]-d[i]
	    if (unixtimes[i+1]<>unixtimes[i]):
		velo[i+1] = dl/(unixtimes[i+1]-unixtimes[i])
	    else:
		velo[i+1]=0

	    if (spm[i]<>0):
		strokelength[i] = dl*60/spm[i]
	    else:
		strokelength[i] = 0.


	velo2 = ewmovingaverage(velo,window_size)
	strokelength2 = ewmovingaverage(strokelength,window_size)
	pace = 500./velo2



	# Create data frame with all necessary data to write to csv
	data = DataFrame({'TimeStamp (sec)':unixtimes,
			  ' Horizontal (meters)': d,
			  ' Cadence (stokes/min)':spm,
			  ' HRCur (bpm)':hr,
			  ' Stroke500mPace (sec/500m)':pace,
			  ' Power (watts)':np.zeros(nr_rows),
			  ' DriveLength (meters)':np.zeros(nr_rows),
			  ' StrokeDistance (meters)':strokelength2,
			  ' DriveTime (ms)':np.zeros(nr_rows),
			  ' StrokeRecoveryTime (ms)':np.zeros(nr_rows),
			  ' AverageDriveForce (lbs)':np.zeros(nr_rows),
			  ' PeakDriveForce (lbs)':np.zeros(nr_rows),
			  ' lapIdx':np.zeros(nr_rows),
			  ' ElapsedTime (sec)':unixtimes-self.activity_starttime
			  })
	
	return data.to_csv(writeFile,index_label='index')


class rower:
    """ This class contains all the personal data about the rower

    * HR threshold values

    * C2 logbook username and password

    * weight category

    """
    
    def __init__(self,hrut2=142,hrut1=146,hrat=160,
		 hrtr=167,hran=180,hrmax=192,
		 c2username="",
		 c2password="",
		 weightcategory="hwt",
		 mc=72.5,
		 strokelength=1.35):
	self.ut2=hrut2
	self.ut1=hrut1
	self.at=hrat
	self.tr=hrtr
	self.an=hran
	self.max=hrmax
	self.c2username=c2username
	self.c2password=c2password
	if (weknowphysics==1):
	    self.rc = rowingphysics.crew(mc=mc,strokelength=strokelength)
	else:
	    self.rc = 0
	if (weightcategory <> "hwt") and (weightcategory <> "lwt"):
	    print "Weightcategory unrecognized. Set to hwt"
	    weightcategory = "hwt"
	    
	self.weightcategory=weightcategory

    def write(self,fileName):
	res = write_obj(self,fileName)


def roweredit(fileName="defaultrower.txt"):
    """ Easy editing or creation of a rower file.
    Mainly for using from the windows command line

    """

    try:
	r = pickle.load(open(fileName))
    except IOError:
	print "Roweredit: File does not exist. Reverting to defaultrower.txt"
	r = getrower()
    except ImportError:
	print "Roweredit: File is not valid. Reverting to defaultrower.txt"
	r = getrower()

    try:
	rc = r.rc
    except AttributeError:
	if (weknowphysics==1):
	    rc = rowingphysics.crew()
	else:
	    rc = 0

    print "Heart Rate Training Bands"
    # hrmax
    print "Your HR max is set to {hrmax} bpm".format(
	hrmax = r.max
	)
    strin = raw_input('Enter HR max (just ENTER to keep {hrmax}):'.format(hrmax=r.max))
    if (strin <> ""):
	try:
	    r.max = int(strin)
	except ValueError:
	    print "Not a valid number. Keeping original value"

    
    # hrut2, hrut1
    print "UT2 zone is between {hrut2} and {hrut1} bpm ({percut2:2.0f}-{percut1:2.0f}% of max HR)".format(
	hrut2 = r.ut2,
	hrut1 = r.ut1,
	percut2 = 100.*r.ut2/r.max,
	percut1 = 100.*r.ut1/r.max
	)
    strin = raw_input('Enter UT2 band lower value (ENTER to keep {hrut2}):'.format(hrut2=r.ut2))
    if (strin <> ""):
	try:
	    r.ut2 = int(strin)
	except ValueError:
    	    print "Not a valid number. Keeping original value"

    strin = raw_input('Enter UT2 band upper value (ENTER to keep {hrut1}):'.format(hrut1=r.ut1))
    if (strin <> ""):
	try:
	    r.ut1 = int(strin)
	except ValueError:
    	    print "Not a valid number. Keeping original value"

    
    print "UT1 zone is between {val1} and {val2} bpm ({perc1:2.0f}-{perc2:2.0f}% of max HR)".format(
	val1 = r.ut1,
	val2 = r.at,
	perc1 = 100.*r.ut1/r.max,
	perc2 = 100.*r.at/r.max
	)

    strin = raw_input('Enter UT1 band upper value (ENTER to keep {hrat}):'.format(hrat=r.at))
    if (strin <> ""):
	try:
	    r.at = int(strin)
	except ValueError:
    	    print "Not a valid number. Keeping original value"

    
    print "AT zone is between {val1} and {val2} bpm ({perc1:2.0f}-{perc2:2.0f}% of max HR)".format(
	val1 = r.at,
	val2 = r.tr,
	perc1 = 100.*r.at/r.max,
	perc2 = 100.*r.tr/r.max
	)

    strin = raw_input('Enter AT band upper value (ENTER to keep {hrtr}):'.format(hrtr=r.tr))
    if (strin <> ""):
	try:
	    r.tr = int(strin)
	except ValueError:
    	    print "Not a valid number. Keeping original value"

    
    
    print "TR zone is between {val1} and {val2} bpm ({perc1:2.0f}-{perc2:2.0f}% of max HR)".format(
	val1 = r.tr,
	val2 = r.an,
	perc1 = 100.*r.tr/r.max,
	perc2 = 100.*r.an/r.max
	)

    strin = raw_input('Enter TR band upper value (ENTER to keep {hran}):'.format(hran=r.an))
    if (strin <> ""):
	try:
	    r.an = int(strin)
	except ValueError:
    	    print "Not a valid number. Keeping original value"


    print ""

    # weightcategory    
    print "Your weight category is set to {weightcategory}.".format(
	weightcategory = r.weightcategory
	)
    strin = raw_input('Enter lwt for Light Weight, hwt for Heavy Weight, or just ENTER: ')
    if (strin <> ""):
	if (strin == 'lwt'):
	    r.weightcategory = strin
	    print "Setting to "+strin
	elif (strin == 'hwt'):
	    r.weightcategory = strin
	    print "Setting to "+strin
	else:
	    print "Value not recognized"

    print ""


    mc = rc.mc
    # weight
    strin = raw_input("Enter weight in kg (or ENTER to keep {mc} kg):".format(
	mc = mc
	))
    if (strin <> ""):
	rc.mc = float(strin)

    # strokelength
    strin = raw_input("Enter strokelength in m (or ENTER to keep {l} m:".format(
	l = rc.strokelength
	))
    if (strin <>""):
	rc.strokelength = float(strin)

    r.rc = rc

    # c2username
    if (r.c2username <> ""):
	print "Your Concept2 username is set to {c2username}.".format(
	    c2username = r.c2username
	)
	strin = raw_input('Enter new username (or just ENTER to keep): ')
	if (strin <> ""):
	    r.c2username = strin


    # c2password
    if (r.c2username == ""):
	print "We don't know your Concept2 username"
	strin = raw_input('Enter new username (or ENTER to skip): ')
	r.c2username = strin

    if (r.c2username <> ""):
	if (r.c2password <> ""):
	    print "We have your Concept2 password."
	    changeyesno = raw_input('Do you want to change/erase your password (y/n)')
	    if changeyesno == "y":
		strin1 = getpass.getpass('Enter new password (or ENTER to erase):')
		if (strin1 <> ""):
		    strin2 = getpass.getpass('Repeat password:')
		    if (strin1 == strin2):
			r.c2password = strin1
		    else:
			print "Error. Not the same."
		if (strin1 == ""):
			print "Forgetting your password"
			r.c2password = ""
	elif (r.c2password == ""):
	    print "We don't have your Concept2 password yet."
	    strin1 = getpass.getpass('Concept2 password (or ENTER to skip):')
	    if (strin1 <> ""):
		strin2 = getpass.getpass('Repeat password:')
		if (strin1 == strin2):
		    r.c2password = strin1
		else:
		    print "Error. Not the same."
    
    


    r.write(fileName)
    
    print "Done"
    return 1

def boatedit(fileName="my1x.txt"):
    """ Easy editing or creation of a boat rigging data file.
    Mainly for using from the windows command line

    """

    try:
	rg = pickle.load(open(fileName))
    except IOError:
	print "Boatedit: File does not exist. Reverting to my1x.txt"
	rg = getrigging()
    except (ImportError,ValueError):
	print "Boatedit: File is not valid. Reverting to my1x.txt"
	rg = getrigging()

    print "Number of rowers"
    # Lin
    print "Your boat has {Nrowers} seats".format(
	Nrowers = rg.Nrowers
	)
    strin = raw_input('Enter number of seats (just ENTER to keep {Nrowers}):'.format(
	Nrowers = rg.Nrowers
	))
    if (strin <> ""):
	try:
	    rg.Nrowers = int(strin)
	except ValueError:
	    print "Not a valid number. Keeping original value"

    print "Rowing or sculling"
    # roworscull
    strin = raw_input('Row (r) or scull (s) - ENTER to keep {roworscull}:'.format(
	roworscull = rg.roworscull
	))
    if (strin == "s"):
	rg.roworscull = 'scull'
    elif (strin == "r"):
	rg.roworscull = 'row'
    

    print "Boat weight"
    # mb
    print "Your {Nrowers} boat weighs {mb} kg".format(
	Nrowers = rg.Nrowers,
	mb = rg.mb
	)
    strin = raw_input('Enter boat weight including cox (just ENTER to keep {mb}):'.format(
	mb = rg.mb
	))
    if (strin <> ""):
	try:
	    rg.mb = float(strin)
	except ValueError:
	    print "Not a valid number. Keeping original value"

    print "Rigging Data"
    # Lin
    print "Your inboard is set to {lin} m".format(
	lin = rg.lin
	)
    strin = raw_input('Enter inboard (just ENTER to keep {lin} m):'.format(
	lin = rg.lin
	))
    if (strin <> ""):
	try:
	    rg.lin = float(strin)
	except ValueError:
	    print "Not a valid number. Keeping original value"

    print "Your scull/oar length is set to {lscull} m".format(
	lscull = rg.lscull
	)
    print "For this number, you need to subtract half of the blade length from the classical oar/scull length measurement"
    strin = raw_input('Enter length (subtract half of blade length, just ENTER to keep {lscull}):'.format(
	lscull = rg.lscull
	))
    if (strin <> ""):
	try:
	    rg.lscull = float(strin)
	except ValueError:
	    print "Not a valid number. Keeping original value"


    if (rg.roworscull == 'row'):
	print "Your spread is set to {spread} m".format(
	    spread = rg.spread
	    )
	strin = raw_input('Enter new spread (or ENTER to keep {spread} m):'.format(
	    spread = rg.spread
	    ))
	if (strin <> ""):
	    try:
		rg.spread = float(spread)
	    except ValueError:
		print "Not a valid number. Keeping original value"
    else:
	print "Your span is set to {span} m".format(
	    span = rg.span
	    )
	strin = raw_input('Enter new span (or ENTER to keep {span} m):'.format(
	    span = rg.span
	    ))
	if (strin <> ""):
	    try:
		rg.span = float(span)
	    except ValueError:
		print "Not a valid number. Keeping original value"
	
    # Blade Area
    print "Your blade area is set to {bladearea} m2 (total blade area per rower, take two blades for scullers)".format(
	bladearea = rg.bladearea
	)
    strin = raw_input('Enter blade area (just ENTER to keep {bladearea} m2):'.format(
	bladearea = rg.bladearea
	))
    if (strin <> ""):
	try:
	    rg.bladearea = float(strin)
	except ValueError:
	    print "Not a valid number. Keeping original value"

    # Catch angle
    catchangledeg = -np.degrees(rg.catchangle)

    print "We define catch angle as follows."
    print " - 0 degrees is a catch with oar shaft perpendicular to the boat"
    print " - 90 degrees is a catch with oar shaft parallel to the boat"
    print " - Use positive values for normal catch angles"
    print "Your catch angle is {catchangledeg} degrees."
    strin = raw_input('Enter catch angle in degrees (or ENTER to keep {catchangledeg}):'.format(
	catchangledeg = catchangledeg
	))
    if (strin <> ""):
	try:
	    rg.catchangle = -np.radians(float(strin))
	except ValueError:
	    print "Not a valid number. Keeping original value"

    write_obj(rg,fileName)
    
    print "Done"
    return 1


class rowingdata:
    """ This is the main class. Read the data from the csv file and do all
    kinds
    of cool stuff with it.

    Usage: row = rowingdata.rowingdata("testdata.csv",rowtype = "Indoor Rower")
           row.plotmeters_all()
	   
    The default rower looks for a defaultrower.txt file. If it is not found,
    it reverts to some arbitrary rower.
    

    """
    
    def __init__(self,readFile,
		 rower=rower(),
		 rowtype="Indoor Rower"):

	try:
	    self.readfilename = readFile.name
	except AttributeError:
	    self.readfilename = readFile
	
	self.readFile = readFile
	self.rower = rower
	self.rowtype = rowtype
	
	sled_df = pd.read_csv(readFile)

	# get the date of the row
	starttime = sled_df.loc[0,'TimeStamp (sec)']
	# using UTC time for now
	self.rowdatetime = datetime.datetime.utcfromtimestamp(starttime)
	
	    	
	# remove the start time from the time stamps
	sled_df['TimeStamp (sec)']=sled_df['TimeStamp (sec)']-sled_df['TimeStamp (sec)'][0]

	number_of_columns = sled_df.shape[1]
	number_of_rows = sled_df.shape[0]

	# these parameters are handy to have available in other routines
	self.number_of_rows = number_of_rows


	# define an additional data frame that will hold the multiple bar plot data and the hr 
	# limit data for the plot, it also holds a cumulative distance column
	# Sander: changed the first row of next line (compared to Greg)
	# Sander: so it will work with my TCX to CSV parsed files
	hr_df = DataFrame({'key': sled_df['TimeStamp (sec)'],
			   'hr_ut2': np.zeros(number_of_rows),
			   'hr_ut1': np.zeros(number_of_rows),
			   'hr_at': np.zeros(number_of_rows),
			   'hr_tr': np.zeros(number_of_rows),
			   'hr_an': np.zeros(number_of_rows),
			   'hr_max': np.zeros(number_of_rows),
			   'lim_ut2': self.rower.ut2,
			   'lim_ut1': self.rower.ut1,
			   'lim_at': self.rower.at,
			   'lim_tr': self.rower.tr,
			   'lim_an': self.rower.an,
			   'lim_max': self.rower.max,
			   'cum_dist':np.zeros(number_of_rows)
			   })

				   
	# merge the two dataframes together
	df = pd.merge(sled_df,hr_df,left_on='TimeStamp (sec)',right_on='key')

	# create the columns containing the data for the colored bar chart
	# attempt to do this in a way that doesn't generate dubious copy warnings
	mask = df[' HRCur (bpm)']<=self.rower.ut2
	df.loc[mask,'hr_ut2'] = df.loc[mask,' HRCur (bpm)']

	mask = (df[' HRCur (bpm)']<=self.rower.ut1)&(df[' HRCur (bpm)']>self.rower.ut2)
	df.loc[mask,'hr_ut1'] = df.loc[mask,' HRCur (bpm)']

	mask = (df[' HRCur (bpm)']<=self.rower.at)&(df[' HRCur (bpm)']>self.rower.ut1)
	df.loc[mask,'hr_at'] = df.loc[mask,' HRCur (bpm)']

	mask = (df[' HRCur (bpm)']<=self.rower.tr)&(df[' HRCur (bpm)']>self.rower.at)
	df.loc[mask,'hr_tr'] = df.loc[mask,' HRCur (bpm)']

	mask = (df[' HRCur (bpm)']<=self.rower.an)&(df[' HRCur (bpm)']>self.rower.tr)
	df.loc[mask,'hr_an'] = df.loc[mask,' HRCur (bpm)']

	mask = (df[' HRCur (bpm)']>self.rower.an)
	df.loc[mask,'hr_max'] = df.loc[mask,' HRCur (bpm)']



	# fill cumulative distance column with cumulative distance
	# ignoring resets to lower distance values
	dl = df[' Horizontal (meters)'].diff()
	nrsteps = np.cumsum(dl<0).max()

	if (nrsteps>0):
	    df['cum_dist'] = np.cumsum(df[' Horizontal (meters)'].diff()[df[' Horizontal (meters)'].diff()>0])+df.ix[0,' Horizontal (meters)']
	else:
	    df['cum_dist'] = df[' Horizontal (meters)']

	# Remove the NaN values from the data frame (in the cum_dist column)
	self.df = df.fillna(method='ffill')

    def getvalues(self,keystring):
	""" Just a tool to get a column of the row data as a numpy array

	You can also just access row.df[keystring] to get a pandas Series

	"""
	
	return self.df[keystring].values

    def write_csv(self,writeFile):
	data = self.df
	try:
	    data = data.drop(['index',
			      'key',
			      'hr_ut2',
			      'hr_ut1',
			      'hr_at',
			      'hr_tr',
			      'hr_an',
			      'hr_max',
			      'lim_ut2',
			      'lim_ut1',
			      'lim_at',
			      'lim_tr',
			      'lim_an',
			      'lim_max',
			      'cum_dist'],1)
	except ValueError:
	    data = data.drop(['key',
			      'hr_ut2',
			      'hr_ut1',
			      'hr_at',
			      'hr_tr',
			      'hr_an',
			      'hr_max',
			      'lim_ut2',
			      'lim_ut1',
			      'lim_at',
			      'lim_tr',
			      'lim_an',
			      'lim_max',
			      'cum_dist'],1)
	    

	return data.to_csv(writeFile,index_label='index')

    def exporttotcx(self,fileName):
	df = self.df

	writetcx.write_tcx(fileName,df,row_date=self.rowdatetime.isoformat())


    def intervalstats(self,separator='|'):
	""" Used to create a nifty text summary, one row for each interval

	Also copies the string to the clipboard (handy!)

	Works for painsled (both iOS and desktop version) because they use
	the lapIdx column

	"""
	
	df = self.df

	intervalnrs = pd.unique(df[' lapIdx'])

	stri = "Workout Details\n"
	stri += "#-{sep}SDist{sep}-Split-{sep}-SPace-{sep}SPM-{sep}AvgHR{sep}MaxHR{sep}DPS-\n".format(
	    sep = separator
	    )

	previousdist = 0.0
	previoustime = 0.0

	for idx in intervalnrs:
	    td = df[df[' lapIdx'] == idx]
	    avghr = td[' HRCur (bpm)'].mean()
	    maxhr = td[' HRCur (bpm)'].max()
	    avgspm = td[' Cadence (stokes/min)'].mean()
	    
	    intervaldistance = td['cum_dist'].max()-previousdist
	    previousdist = td['cum_dist'].max()

	    intervalduration = td['TimeStamp (sec)'].max()-previoustime
	    previoustime = td['TimeStamp (sec)'].max()
	    
	    intervalpace = 500.*intervalduration/intervaldistance
	    avgdps = intervaldistance/(intervalduration*avgspm/60.)
	    if isnan(avgdps) or isinf(avgdps):
		avgdps = 0


	    stri += interval_string(idx,intervaldistance,intervalduration,
				    intervalpace,avgspm,
				    avghr,maxhr,avgdps,
				    separator=separator)
	    


	return stri

    def add_bearing(self,window_size=20):
	""" Adds bearing. Only works if long and lat values are known

	"""
	nr_of_rows = self.number_of_rows
	df = self.df

	bearing = np.zeros(nr_of_rows)
	
	for i in range(nr_of_rows-1):
	    try:
		long1 = df.ix[i,' longitude']
		lat1 = df.ix[i,' latitude']
		long2 = df.ix[i+1,' longitude']
		lat2 = df.ix[i+1,' latitude']
	    except KeyError:
		long1 = 0
		lat1 = 0
		long2 = 0
		lat2 = 0
	    res = geo_distance(lat1,long1,lat2,long2)
	    bearing[i] = res[1]

	bearing2 = ewmovingaverage(bearing,window_size)


	df['bearing'] = 0
	df['bearing'] = bearing2

	self.df = df

    def add_wind(self,vwind,winddirection,units='m'):
	# beaufort
	if (units == 'b'):
	    vwind = 0.837*vwind**(3./2.)
	# knots
	if (units == 'k'):
	    vwind = vwind*1.994

	df = self.df

	df['vwind'] = vwind
	df['winddirection'] = winddirection

	self.df = df
	    
    def otw_setpower(self,skiprows=0,rg=getrigging()):
	""" Adds power from rowing physics calculations to OTW result

	For now, works only in singles

	"""

	print "EXPERIMENTAL"
	
	nr_of_rows = self.number_of_rows
	rows_mod = skiprows+1
	df = self.df
	df['nowindpace'] = 300

	# creating a rower and rigging for now
	# in future this must come from rowingdata.rower and rowingdata.rigging
	r = self.rower.rc

	# this is slow ... need alternative (read from table)
	for i in tqdm(range(nr_of_rows)):
	    p = df.ix[i,' Stroke500mPace (sec/500m)']
	    spm = df.ix[i,' Cadence (stokes/min)']
	    r.tempo = spm
	    drivetime = 60.*1000./spm  # in milliseconds
	    if (p != 0) & (spm != 0) & (p<210):
		velo = 500./p
		try:
		    vwind = df.ix[i,'vwind']
		    winddirection = df.ix[i,'winddirection']
		    bearing = df.ix[i,'bearing']
		except ValueError:
		    vwind = 0.0
		    winddirection = 0.0
		    bearing = 0.0
		if (i % rows_mod == 0):
		    res = phys_getpower(velo,r,rg,bearing,vwind,winddirection)
		else:
		    res = [np.nan,np.nan,np.nan,np.nan]
		df.ix[i,' Power (watts)'] = res[0]
		df.ix[i,' AverageDriveForce (lbs)'] = res[2]/lbstoN
		df.ix[i,' DriveTime (ms)'] = res[1]*drivetime
		df.ix[i,' StrokeRecoveryTime (ms)'] = (1-res[1])*drivetime
		df.ix[i,' DriveLength (meters)'] = r.strokelength
		df.ix[i,'nowindpace'] = res[3]
		# update_progress(i,nr_of_rows)

	    else:
		velo = 0.0

	self.df = df.interpolate()

    def summary(self,separator='|'):
	""" Creates a nifty text string that contains the key data for the row
	and copies it to the clipboard

	"""
	
	df = self.df

	# total dist, total time, avg pace, avg hr, max hr, avg dps

	totaldist = df['cum_dist'].max()
	totaltime = df['TimeStamp (sec)'].max()-df['TimeStamp (sec)'].min()
	totaltime = totaltime+df.ix[0,' ElapsedTime (sec)']
	avgpace = 500*totaltime/totaldist
	avghr = df[' HRCur (bpm)'].mean()
	maxhr = df[' HRCur (bpm)'].max()
	avgspm = df[' Cadence (stokes/min)'].mean()
	avgdps = totaldist/(totaltime*avgspm/60.)


	stri = summarystring(totaldist,totaltime,avgpace,avgspm,
			     avghr,maxhr,avgdps,
			     readFile=self.readFile,
			     separator=separator)



	return stri

    def allstats(self,separator='|'):
	""" Creates a nice text summary, both overall summary and a one line
	per interval summary

	Works for painsled (both iOS and desktop)

	Also copies the string to the clipboard (handy!)

	"""

	stri = self.summary(separator=separator)+self.intervalstats(separator=separator)


	return stri


    def plotmeters_erg(self):
	""" Creates two images containing interesting plots

	x-axis is distance

	Used with painsled (erg) data
	

	"""
	
	df = self.df

	# distance increments for bar chart
	dist_increments = -df.ix[:,'cum_dist'].diff()
	dist_increments[0] = dist_increments[1]
	

	fig1 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- HR / Pace / Rate / Power"

	# First panel, hr
	ax1 = fig1.add_subplot(4,1,1)
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut2'],
		width = dist_increments,
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut1'],
		width = dist_increments,
		color='y',ec='y')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_at'],
		width = dist_increments,
		color='g',ec='g')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_tr'],
		width = dist_increments,
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_an'],
		width = dist_increments,
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_max'],
		width = dist_increments,
		color='r',ec='r')

	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_max'],color='k')

	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_dist = int(df.ix[df.shape[0]-1,'cum_dist'])

	ax1.axis([0,end_dist,100,1.1*self.rower.max])
	ax1.set_xticks(range(1000,end_dist,1000))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,200,10))
	ax1.set_title(fig_title)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(4,1,2)
	ax2.plot(df.ix[:,'cum_dist'],df.ix[:,' Stroke500mPace (sec/500m)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,160])
	ax2.axis([0,end_dist,yrange[1],yrange[0]])
	ax2.set_xticks(range(1000,end_dist,1000))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(145,95,-5))
	grid(True)
	majorTickFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.yaxis.set_major_formatter(majorTickFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(4,1,3)
	ax3.plot(df.ix[:,'cum_dist'],df.ix[:,' Cadence (stokes/min)'])
	ax3.axis([0,end_dist,14,40])
	ax3.set_xticks(range(1000,end_dist,1000))
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))

	grid(True)

	# Fourth Panel, watts
	ax4 = fig1.add_subplot(4,1,4)
	ax4.plot(df.ix[:,'cum_dist'],df.ix[:,' Power (watts)'])
	yrange = y_axis_range(df.ix[:,' Power (watts)'],
			      ultimate=[50,550])
	ax4.axis([0,end_dist,yrange[0],yrange[1]])
	ax4.set_xticks(range(1000,end_dist,1000))
	ax4.set_xlabel('Dist (km)')
	ax4.set_ylabel('Watts')
#	ax4.set_yticks(range(150,450,50))
	grid(True)
	majorKmFormatter = FuncFormatter(format_dist_tick)
	majorLocator = (1000)
	ax4.xaxis.set_major_formatter(majorKmFormatter)

	plt.subplots_adjust(hspace=0)
	
	fig2 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- Stroke Metrics"
	
	# Top plot is pace
	ax5 = fig2.add_subplot(4,1,1)
	ax5.plot(df.ix[:,'cum_dist'],df.ix[:,' Stroke500mPace (sec/500m)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,160])
	ax5.axis([0,end_dist,yrange[1],yrange[0]])
	ax5.set_xticks(range(1000,end_dist,1000))
	ax5.set_ylabel('(sec/500)')
#	ax5.set_yticks(range(175,95,-10))
	grid(True)
	ax5.set_title(fig_title)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax5.yaxis.set_major_formatter(majorFormatter)
	
	# next we plot the drive length
	ax6 = fig2.add_subplot(4,1,2)
	ax6.plot(df.ix[:,'cum_dist'],df.ix[:,' DriveLength (meters)'])
	yrange = y_axis_range(df.ix[:,' DriveLength (meters)'],
			      ultimate = [1,15])
	ax6.axis([0,end_dist,yrange[0],yrange[1]])
	ax6.set_xticks(range(1000,end_dist,1000))
	ax6.set_ylabel('Drive Len(m)')
#	ax6.set_yticks(np.arange(1.,2.,0.05))
	grid(True)

	# next we plot the drive time and recovery time
	ax7 = fig2.add_subplot(4,1,3)
	ax7.plot(df.ix[:,'cum_dist'],df.ix[:,' DriveTime (ms)']/1000.)
	ax7.plot(df.ix[:,'cum_dist'],df.ix[:,' StrokeRecoveryTime (ms)']/1000.)
	s = np.concatenate((df.ix[:,' DriveTime (ms)'].values/1000.,
			   df.ix[:,' StrokeRecoveryTime (ms)'].values/1000.))
	yrange = y_axis_range(s,ultimate=[0.5,4])
	
	ax7.axis([0,end_dist,yrange[0],yrange[1]])
	ax7.set_xticks(range(1000,end_dist,1000))
	ax7.set_ylabel('Drv / Rcv Time (s)')
#	ax7.set_yticks(np.arange(0.2,3.0,0.2))
	grid(True)

	# Peak and average force
	ax8 = fig2.add_subplot(4,1,4)
	ax8.plot(df.ix[:,'cum_dist'],
		 df.ix[:,' AverageDriveForce (lbs)']*lbstoN)
	ax8.plot(df.ix[:,'cum_dist'],
		 df.ix[:,' PeakDriveForce (lbs)']*lbstoN)
	s = np.concatenate((df.ix[:,' AverageDriveForce (lbs)'].values*lbstoN,
			   df.ix[:,' PeakDriveForce (lbs)'].values*lbstoN))
	yrange = y_axis_range(s,ultimate=[0,1000])

	ax8.axis([0,end_dist,yrange[0],yrange[1]])
	ax8.set_xticks(range(1000,end_dist,1000))
	ax8.set_xlabel('Dist (m)')
	ax8.set_ylabel('Force (N)')
#	ax8.set_yticks(range(25,300,25))
	grid(True)
	majorLocator = (1000)
	ax8.xaxis.set_major_formatter(majorKmFormatter)
	

	plt.subplots_adjust(hspace=0)

	plt.show()
	print "done"
    
    def plottime_erg(self):
	""" Creates two images containing interesting plots

	x-axis is time

	Used with painsled (erg) data
	

	"""

	df = self.df

	# time increments for bar chart
	time_increments = df.ix[:,' ElapsedTime (sec)'].diff()
	time_increments[0] = time_increments[1]
	


	fig1 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- HR / Pace / Rate "

	# First panel, hr
	ax1 = fig1.add_subplot(4,1,1)
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut2'],
		width=time_increments,
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut1'],
		width=time_increments,
		color='y',ec='y')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_at'],
		width=time_increments,
		color='g',ec='g')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_tr'],
		width=time_increments,
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_an'],
		width=time_increments,
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_max'],
		width=time_increments,
		color='r',ec='r')

	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_max'],color='k')
	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])

	ax1.axis([0,end_time,100,1.1*self.rower.max])
	ax1.set_xticks(range(0,end_time,300))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,200,10))
	ax1.set_title(fig_title)
	timeTickFormatter = NullFormatter()
	ax1.xaxis.set_major_formatter(timeTickFormatter)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(4,1,2)
	ax2.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' Stroke500mPace (sec/500m)'])

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,160])
	ax2.axis([0,end_time,yrange[1],yrange[0]])
	ax2.set_xticks(range(0,end_time,300))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(145,90,-5))
	# ax2.set_title('Pace')
	grid(True)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.xaxis.set_major_formatter(timeTickFormatter)
	ax2.yaxis.set_major_formatter(majorFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(4,1,3)
	ax3.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Cadence (stokes/min)'])
#	rate_ewma = pd.ewma
	ax3.axis([0,end_time,14,40])
	ax3.set_xticks(range(0,end_time,300))
	ax3.set_xlabel('Time (sec)')
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))
	# ax3.set_title('Rate')
	ax3.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)

	# Fourth Panel, watts
	ax4 = fig1.add_subplot(4,1,4)
	ax4.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Power (watts)'])
	yrange = y_axis_range(df.ix[:,' Power (watts)'],
			      ultimate=[50,555])
	ax4.axis([0,end_time,yrange[0],yrange[1]])
	ax4.set_xticks(range(0,end_time,300))
	ax4.set_xlabel('Time (h:m)')
	ax4.set_ylabel('Watts')
#	ax4.set_yticks(range(150,450,50))
	# ax4.set_title('Power')
	grid(True)
	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax4.xaxis.set_major_formatter(majorTimeFormatter)

	plt.subplots_adjust(hspace=0)
	
	fig2 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- Stroke Metrics"

	# Top plot is pace
	ax5 = fig2.add_subplot(4,1,1)
	ax5.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' Stroke500mPace (sec/500m)'])

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,160])
	ax5.axis([0,end_time,yrange[1],yrange[0]])
	ax5.set_xticks(range(0,end_time,300))
	ax5.set_ylabel('(sec/500)')
#	ax5.set_yticks(range(145,90,-5))
	grid(True)
	ax5.set_title(fig_title)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax5.xaxis.set_major_formatter(timeTickFormatter)
	ax5.yaxis.set_major_formatter(majorFormatter)

	# next we plot the drive length
	ax6 = fig2.add_subplot(4,1,2)
	ax6.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' DriveLength (meters)'])
	yrange = y_axis_range(df.ix[:,' DriveLength (meters)'],
			      ultimate = [1.0,15])
	ax6.axis([0,end_time,yrange[0],yrange[1]])
	ax6.set_xticks(range(0,end_time,300))
	ax6.set_xlabel('Time (sec)')
	ax6.set_ylabel('Drive Len(m)')
#	ax6.set_yticks(np.arange(1.35,1.6,0.05))
	ax6.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)

	# next we plot the drive time and recovery time
	ax7 = fig2.add_subplot(4,1,3)
	ax7.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' DriveTime (ms)']/1000.)
	ax7.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' StrokeRecoveryTime (ms)']/1000.)
	s = np.concatenate((df.ix[:,' DriveTime (ms)'].values/1000.,
			   df.ix[:,' StrokeRecoveryTime (ms)'].values/1000.))
	yrange = y_axis_range(s,ultimate=[0.5,4])
	
	
	ax7.axis([0,end_time,yrange[0],yrange[1]])
	ax7.set_xticks(range(0,end_time,300))
	ax7.set_xlabel('Time (sec)')
	ax7.set_ylabel('Drv / Rcv Time (s)')
#	ax7.set_yticks(np.arange(0.2,3.0,0.2))
	ax7.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)

	# Peak and average force
	ax8 = fig2.add_subplot(4,1,4)
	ax8.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' AverageDriveForce (lbs)']*lbstoN)
	ax8.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' PeakDriveForce (lbs)']*lbstoN)
	s = np.concatenate((df.ix[:,' AverageDriveForce (lbs)'].values*lbstoN,
			   df.ix[:,' PeakDriveForce (lbs)'].values*lbstoN))
	yrange = y_axis_range(s,ultimate=[0,1000])
	
	ax8.axis([0,end_time,yrange[0],yrange[1]])
	ax8.set_xticks(range(0,end_time,300))
	ax8.set_xlabel('Time (h:m)')
	ax8.set_ylabel('Force (N)')
#	ax8.set_yticks(range(25,300,25))
	# ax4.set_title('Power')
	grid(True)
	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax8.xaxis.set_major_formatter(majorTimeFormatter)


	plt.subplots_adjust(hspace=0)

	plt.show()

	self.piechart()
	
	print "done"

    def get_metersplot_otw(self,title):
	df = self.df

	# distance increments for bar chart
	dist_increments = -df.ix[:,'cum_dist'].diff()
	dist_increments[0] = dist_increments[1]
	

	#	fig1 = plt.figure(figsize=(12,10))
	fig1 = figure.Figure(figsize=(12,10))
	fig_title = title

	# First panel, hr
	ax1 = fig1.add_subplot(3,1,1)
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut2'],
		width = dist_increments,align='edge',
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut1'],
		width = dist_increments,align='edge',
		color='y',ec='y')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_at'],
		width = dist_increments,align='edge',
		color='g',ec='g')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_tr'],
		width = dist_increments,align='edge',
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_an'],
		width = dist_increments,align='edge',
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_max'],
		width=dist_increments,align='edge',
		color='r',ec='r')

	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_max'],color='k')

	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_dist = int(df.ix[df.shape[0]-1,'cum_dist'])

	ax1.axis([0,end_dist,100,1.1*self.rower.max])
	ax1.set_xticks(range(1000,end_dist,1000))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,200,10))
	ax1.set_title(fig_title)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(3,1,2)
	ax2.plot(df.ix[:,'cum_dist'],df.ix[:,' Stroke500mPace (sec/500m)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate=[85,190])
	
	ax2.axis([0,end_dist,yrange[1],yrange[0]])
	ax2.set_xticks(range(1000,end_dist,1000))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(175,95,-10))
	grid(True)
	majorTickFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.yaxis.set_major_formatter(majorTickFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(3,1,3)
	ax3.plot(df.ix[:,'cum_dist'],df.ix[:,' Cadence (stokes/min)'])
	ax3.axis([0,end_dist,14,40])
	ax3.set_xticks(range(1000,end_dist,1000))
	ax3.set_xlabel('Distance (m)')
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))

	grid(True)


	plt.subplots_adjust(hspace=0)

	return fig1

    def get_timeplot_otw(self,title):
	df = self.df

	# time increments for bar chart
	time_increments = df.ix[:,' ElapsedTime (sec)'].diff()
	time_increments[0] = time_increments[1]
	


	fig1 = plt.figure(figsize=(12,10))
	
	fig_title = title

	# First panel, hr
	ax1 = fig1.add_subplot(3,1,1)
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut2'],
		width=time_increments,
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut1'],
		width=time_increments,
		color='y',ec='y')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_at'],
		width=time_increments,
		color='g',ec='g')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_tr'],
		width=time_increments,
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_an'],
		width=time_increments,
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_max'],
		width=time_increments,
		color='r',ec='r')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_max'],color='k')
	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	ax1.axis([0,end_time,100,1.1*self.rower.max])
	ax1.set_xticks(range(0,end_time,300))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,190,10))
	ax1.set_title(fig_title)
	timeTickFormatter = NullFormatter()
	ax1.xaxis.set_major_formatter(timeTickFormatter)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(3,1,2)
	ax2.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Stroke500mPace (sec/500m)'])
	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,190])
	ax2.axis([0,end_time,yrange[1],yrange[0]])
	ax2.set_xticks(range(0,end_time,300))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(175,90,-5))
	# ax2.set_title('Pace')
	grid(True)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.xaxis.set_major_formatter(timeTickFormatter)
	ax2.yaxis.set_major_formatter(majorFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(3,1,3)
	ax3.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Cadence (stokes/min)'])
#	rate_ewma = pd.ewma(df,span=20)
#	ax3.plot(rate_ewma.ix[:,'TimeStamp (sec)'],
#		 rate_ewma.ix[:,' Cadence (stokes/min)'])
	ax3.axis([0,end_time,14,40])
	ax3.set_xticks(range(0,end_time,300))
	ax3.set_xlabel('Time (sec)')
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))
	# ax3.set_title('Rate')
	ax3.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)


	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax3.set_xlabel('Time (h:m)')
	ax3.xaxis.set_major_formatter(majorTimeFormatter)
	plt.subplots_adjust(hspace=0)

	return fig1

    def get_pacehrplot(self,title):
	df = self.df

	t = df.ix[:,' ElapsedTime (sec)']
	p = df.ix[:,' Stroke500mPace (sec/500m)']
	hr = df.ix[:,' HRCur (bpm)']
	end_time = int(df.ix[df.shape[0]-1,' ElapsedTime (sec)'])

	fig, ax1 = plt.subplots(figsize=(5,4))

	ax1.plot(t,p,'b-')
	ax1.set_xlabel('Time (h:m)')
	ax1.set_ylabel('(sec/500)')

	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,190])
	plt.axis([0,end_time,yrange[1],yrange[0]])

	ax1.set_xticks(range(1000,end_time,1000))
	ax1.set_yticks(range(185,90,-10))
	ax1.set_title(title)
	plt.grid(True)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	timeTickFormatter = NullFormatter()
	
	ax1.yaxis.set_major_formatter(majorFormatter)

	for tl in ax1.get_yticklabels():
	    tl.set_color('b')

	ax2 = ax1.twinx()
	ax2.plot(t,hr,'r-')
	ax2.set_ylabel('Heart Rate',color='r')
	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax2.xaxis.set_major_formatter(majorTimeFormatter)
	ax2.patch.set_alpha(0.0)
	for tl in ax2.get_yticklabels():
	    tl.set_color('r')
    
	plt.subplots_adjust(hspace=0)

	return fig



    def get_paceplot(self,title):
	df = self.df

	# time increments for bar chart
	time_increments = df.ix[:,'TimeStamp (sec)'].diff()
	time_increments[0] = time_increments[1]
	
	end_dist = int(df.ix[df.shape[0]-1,'cum_dist'])
	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])


	t = df.ix[:,' ElapsedTime (sec)']
	p = df.ix[:,' Stroke500mPace (sec/500m)']
	hr = df.ix[:,' HRCur (bpm)']

	fig, ax1 = plt.subplots()

	ax1.plot(t,p,'b-')
	ax1.set_xlabel('Time')
	ax1.set_ylabel('Pace (sec/500)')

	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,190])
	plt.axis([0,end_time,yrange[1],yrange[0]])

	ax1.set_xticks(range(1000,end_time,1000))
	ax1.set_yticks(range(185,90,-10))
	ax1.set_title(title)
	grid(True)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	timeTickFormatter = NullFormatter()
	
	ax1.yaxis.set_major_formatter(majorFormatter)
	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax1.xaxis.set_major_formatter(majorTimeFormatter)

	for tl in ax1.get_yticklabels():
	    tl.set_color('b')

	ax2 = ax1.twinx()
	ax2.plot(t,hr,'r-')
	ax2.set_ylabel('Heart Rate',color='r')

	for tl in ax2.get_yticklabels():
	    tl.set_color('r')

	return fig

    def get_metersplot_erg(self,title):

	df = self.df

	# distance increments for bar chart
	dist_increments = -df.ix[:,'cum_dist'].diff()
	dist_increments[0] = dist_increments[1]
	

	fig1 = plt.figure(figsize=(12,10))

	fig_title = title

	# First panel, hr
	ax1 = fig1.add_subplot(4,1,1)
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut2'],
		width = dist_increments,
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut1'],
		width = dist_increments,
		color='y',ec='y')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_at'],
		width = dist_increments,
		color='g',ec='g')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_tr'],
		width = dist_increments,
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_an'],
		width = dist_increments,
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_max'],
		width = dist_increments,
		color='r',ec='r')

	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_max'],color='k')

	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_dist = int(df.ix[df.shape[0]-1,'cum_dist'])

	ax1.axis([0,end_dist,100,1.1*self.rower.max])
	ax1.set_xticks(range(1000,end_dist,1000))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,200,10))
	ax1.set_title(fig_title)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(4,1,2)
	ax2.plot(df.ix[:,'cum_dist'],df.ix[:,' Stroke500mPace (sec/500m)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,160])
	ax2.axis([0,end_dist,yrange[1],yrange[0]])
	ax2.set_xticks(range(1000,end_dist,1000))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(145,95,-5))
	grid(True)
	majorTickFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.yaxis.set_major_formatter(majorTickFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(4,1,3)
	ax3.plot(df.ix[:,'cum_dist'],df.ix[:,' Cadence (stokes/min)'])
	ax3.axis([0,end_dist,14,40])
	ax3.set_xticks(range(1000,end_dist,1000))
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))

	grid(True)

	# Fourth Panel, watts
	ax4 = fig1.add_subplot(4,1,4)
	ax4.plot(df.ix[:,'cum_dist'],df.ix[:,' Power (watts)'])
	yrange = y_axis_range(df.ix[:,' Power (watts)'],
			      ultimate=[50,550])
	ax4.axis([0,end_dist,yrange[0],yrange[1]])
	ax4.set_xticks(range(1000,end_dist,1000))
	ax4.set_xlabel('Dist (km)')
	ax4.set_ylabel('Watts')
#	ax4.set_yticks(range(150,450,50))
	grid(True)
	majorKmFormatter = FuncFormatter(format_dist_tick)
	majorLocator = (1000)
	ax4.xaxis.set_major_formatter(majorKmFormatter)

	plt.subplots_adjust(hspace=0)

	return(fig1)


    def get_timeplot_erg(self,title):


	df = self.df

	# time increments for bar chart
	time_increments = df.ix[:,' ElapsedTime (sec)'].diff()
	time_increments[0] = time_increments[1]
	


	fig1 = plt.figure(figsize=(12,10))
	
	fig_title = title

	# First panel, hr
	ax1 = fig1.add_subplot(4,1,1)
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut2'],
		width=time_increments,
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut1'],
		width=time_increments,
		color='y',ec='y')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_at'],
		width=time_increments,
		color='g',ec='g')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_tr'],
		width=time_increments,
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_an'],
		width=time_increments,
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_max'],
		width=time_increments,
		color='r',ec='r')

	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_max'],color='k')
	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])

	ax1.axis([0,end_time,100,1.1*self.rower.max])
	ax1.set_xticks(range(0,end_time,300))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,200,10))
	ax1.set_title(fig_title)
	timeTickFormatter = NullFormatter()
	ax1.xaxis.set_major_formatter(timeTickFormatter)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(4,1,2)
	ax2.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' Stroke500mPace (sec/500m)'])

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,160])
	ax2.axis([0,end_time,yrange[1],yrange[0]])
	ax2.set_xticks(range(0,end_time,300))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(145,90,-5))
	# ax2.set_title('Pace')
	grid(True)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.xaxis.set_major_formatter(timeTickFormatter)
	ax2.yaxis.set_major_formatter(majorFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(4,1,3)
	ax3.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Cadence (stokes/min)'])
#	rate_ewma = pd.ewma
	ax3.axis([0,end_time,14,40])
	ax3.set_xticks(range(0,end_time,300))
	ax3.set_xlabel('Time (sec)')
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))
	# ax3.set_title('Rate')
	ax3.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)

	# Fourth Panel, watts
	ax4 = fig1.add_subplot(4,1,4)
	ax4.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Power (watts)'])
	yrange = y_axis_range(df.ix[:,' Power (watts)'],
			      ultimate=[50,555])
	ax4.axis([0,end_time,yrange[0],yrange[1]])
	ax4.set_xticks(range(0,end_time,300))
	ax4.set_xlabel('Time (h:m)')
	ax4.set_ylabel('Watts')
#	ax4.set_yticks(range(150,450,50))
	# ax4.set_title('Power')
	grid(True)
	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax4.xaxis.set_major_formatter(majorTimeFormatter)

	plt.subplots_adjust(hspace=0)
	

#	plt.show()

#	self.piechart()
	
	return(fig1)

    def plottime_otwpower(self):
	""" Creates two images containing interesting plots

	x-axis is time

	Used with painsled (erg) data
	

	"""

	df = self.df

	# time increments for bar chart
	time_increments = df.ix[:,' ElapsedTime (sec)'].diff()
	time_increments[0] = time_increments[1]
	


	fig1 = plt.figure(figsize=(12,10))

	fig_title = "Input File:  "+self.readfilename+" --- HR / Pace / Rate "

	# First panel, hr
	ax1 = fig1.add_subplot(4,1,1)
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut2'],
		width=time_increments,
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut1'],
		width=time_increments,
		color='y',ec='y')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_at'],
		width=time_increments,
		color='g',ec='g')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_tr'],
		width=time_increments,
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_an'],
		width=time_increments,
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_max'],
		width=time_increments,
		color='r',ec='r')

	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_max'],color='k')
	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])

	ax1.axis([0,end_time,100,1.1*self.rower.max])
	ax1.set_xticks(range(0,end_time,300))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,200,10))
	ax1.set_title(fig_title)
	timeTickFormatter = NullFormatter()
	ax1.xaxis.set_major_formatter(timeTickFormatter)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(4,1,2)
	ax2.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' Stroke500mPace (sec/500m)'])

	ax2.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,'nowindpace'])

	ax2.legend(['Pace','Wind corrected pace'],prop={'size':10})
	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])

	s = np.concatenate((df.ix[:,' Stroke500mPace (sec/500m)'].values,
			   df.ix[:,'nowindpace'].values))
	yrange = y_axis_range(s,ultimate=[100,210])

	ax2.axis([0,end_time,yrange[1],yrange[0]])
	ax2.set_xticks(range(0,end_time,300))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(145,90,-5))
	# ax2.set_title('Pace')
	grid(True)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.xaxis.set_major_formatter(timeTickFormatter)
	ax2.yaxis.set_major_formatter(majorFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(4,1,3)
	ax3.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Cadence (stokes/min)'])
#	rate_ewma = pd.ewma
	ax3.axis([0,end_time,14,40])
	ax3.set_xticks(range(0,end_time,300))
	ax3.set_xlabel('Time (sec)')
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))
	# ax3.set_title('Rate')
	ax3.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)

	# Fourth Panel, watts
	ax4 = fig1.add_subplot(4,1,4)
	ax4.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Power (watts)'])
	yrange = y_axis_range(df.ix[:,' Power (watts)'],
			      ultimate=[50,555])
	ax4.axis([0,end_time,yrange[0],yrange[1]])
	ax4.set_xticks(range(0,end_time,300))
	ax4.set_xlabel('Time (h:m)')
	ax4.set_ylabel('Watts')
#	ax4.set_yticks(range(150,450,50))
	# ax4.set_title('Power')
	grid(True)
	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax4.xaxis.set_major_formatter(majorTimeFormatter)

	plt.subplots_adjust(hspace=0)
	
	fig2 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- Stroke Metrics"

	# Top plot is pace
	ax5 = fig2.add_subplot(4,1,1)
	ax5.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' Stroke500mPace (sec/500m)'])

	ax5.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,'nowindpace'])
	ax5.legend(['Pace','Wind corrected pace'],prop={'size':10})

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])

	s = np.concatenate((df.ix[:,' Stroke500mPace (sec/500m)'].values,
			   df.ix[:,'nowindpace'].values))
	yrange = y_axis_range(s,ultimate=[100,210])

	ax5.axis([0,end_time,yrange[1],yrange[0]])
	ax5.set_xticks(range(0,end_time,300))
	ax5.set_ylabel('(sec/500)')
#	ax5.set_yticks(range(145,90,-5))
	grid(True)
	ax5.set_title(fig_title)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax5.xaxis.set_major_formatter(timeTickFormatter)
	ax5.yaxis.set_major_formatter(majorFormatter)

	# next we plot the drive length
	ax6 = fig2.add_subplot(4,1,2)
	ax6.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' DriveLength (meters)'])
	yrange = y_axis_range(df.ix[:,' DriveLength (meters)'],
			      ultimate = [1.0,15])
	ax6.axis([0,end_time,yrange[0],yrange[1]])
	ax6.set_xticks(range(0,end_time,300))
	ax6.set_xlabel('Time (sec)')
	ax6.set_ylabel('Drive Len(m)')
#	ax6.set_yticks(np.arange(1.35,1.6,0.05))
	ax6.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)

	# next we plot the drive time and recovery time
	ax7 = fig2.add_subplot(4,1,3)
	ax7.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' DriveTime (ms)']/1000.)
	ax7.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' StrokeRecoveryTime (ms)']/1000.)
	s = np.concatenate((df.ix[:,' DriveTime (ms)'].values/1000.,
			   df.ix[:,' StrokeRecoveryTime (ms)'].values/1000.))
	yrange = y_axis_range(s,ultimate=[0.5,4])
	
	
	ax7.axis([0,end_time,yrange[0],yrange[1]])
	ax7.set_xticks(range(0,end_time,300))
	ax7.set_xlabel('Time (sec)')
	ax7.set_ylabel('Drv / Rcv Time (s)')
#	ax7.set_yticks(np.arange(0.2,3.0,0.2))
	ax7.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)

	# Peak and average force
	ax8 = fig2.add_subplot(4,1,4)
	ax8.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' AverageDriveForce (lbs)']*lbstoN)
	ax8.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' PeakDriveForce (lbs)']*lbstoN)
	s = np.concatenate((df.ix[:,' AverageDriveForce (lbs)'].values*lbstoN,
			   df.ix[:,' PeakDriveForce (lbs)'].values*lbstoN))
	yrange = y_axis_range(s,ultimate=[0,1000])
	
	ax8.axis([0,end_time,yrange[0],yrange[1]])
	ax8.set_xticks(range(0,end_time,300))
	ax8.set_xlabel('Time (h:m)')
	ax8.set_ylabel('Force (N)')
#	ax8.set_yticks(range(25,300,25))
	# ax4.set_title('Power')
	grid(True)
	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax8.xaxis.set_major_formatter(majorTimeFormatter)


	plt.subplots_adjust(hspace=0)

	plt.show()

	self.piechart()
	
	print "done"

    def plottime_hr(self):
	""" Creates a HR vs time plot

	"""
	
	df = self.df
	fig1 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- HR "

	# First panel, hr
	ax1 = fig1.add_subplot(1,1,1)
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut2'],color='gray', ec='gray')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut1'],color='y',ec='y')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_at'],color='g',ec='g')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_tr'],color='blue',ec='blue')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_an'],color='violet',ec='violet')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_max'],color='r',ec='r')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_max'],color='k')
	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	ax1.axis([0,end_time,100,1.1*self.rower.max])
	ax1.set_xticks(range(0,end_time,300))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,190,10))
	ax1.set_title(fig_title)
	timeTickFormatter = NullFormatter()
	ax1.xaxis.set_major_formatter(timeTickFormatter)

	grid(True)
	plt.show()

    def plotmeters_otw(self):
	""" Creates two images containing interesting plots

	x-axis is distance

	Used with OTW data (no Power plot)
	

	"""

	df = self.df

	# distance increments for bar chart
	dist_increments = -df.ix[:,'cum_dist'].diff()
	dist_increments[0] = dist_increments[1]
	

	fig1 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- HR / Pace / Rate / Power"

	# First panel, hr
	ax1 = fig1.add_subplot(3,1,1)
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut2'],
		width = dist_increments,align='edge',
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_ut1'],
		width = dist_increments,align='edge',
		color='y',ec='y')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_at'],
		width = dist_increments,align='edge',
		color='g',ec='g')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_tr'],
		width = dist_increments,align='edge',
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_an'],
		width = dist_increments,align='edge',
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'cum_dist'],df.ix[:,'hr_max'],
		width=dist_increments,align='edge',
		color='r',ec='r')

	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'cum_dist'],df.ix[:,'lim_max'],color='k')

	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_dist = int(df.ix[df.shape[0]-1,'cum_dist'])

	ax1.axis([0,end_dist,100,1.1*self.rower.max])
	ax1.set_xticks(range(1000,end_dist,1000))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,200,10))
	ax1.set_title(fig_title)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(3,1,2)
	ax2.plot(df.ix[:,'cum_dist'],df.ix[:,' Stroke500mPace (sec/500m)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate=[85,190])
	
	ax2.axis([0,end_dist,yrange[1],yrange[0]])
	ax2.set_xticks(range(1000,end_dist,1000))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(175,95,-10))
	grid(True)
	majorTickFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.yaxis.set_major_formatter(majorTickFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(3,1,3)
	ax3.plot(df.ix[:,'cum_dist'],df.ix[:,' Cadence (stokes/min)'])
	ax3.axis([0,end_dist,14,40])
	ax3.set_xticks(range(1000,end_dist,1000))
	ax3.set_xlabel('Distance (m)')
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))

	grid(True)


	plt.subplots_adjust(hspace=0)
	
	fig2 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- Stroke Metrics"
	
	# Top plot is pace
	ax5 = fig2.add_subplot(2,1,1)
	ax5.plot(df.ix[:,'cum_dist'],df.ix[:,' Stroke500mPace (sec/500m)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,190])
	ax5.axis([0,end_dist,yrange[1],yrange[0]])
	ax5.set_xticks(range(1000,end_dist,1000))
	ax5.set_ylabel('(sec/500)')
#	ax5.set_yticks(range(175,95,-10))
	grid(True)
	ax5.set_title(fig_title)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax5.yaxis.set_major_formatter(majorFormatter)
	
	# next we plot the stroke distance
	ax6 = fig2.add_subplot(2,1,2)
	ax6.plot(df.ix[:,'cum_dist'],df.ix[:,' StrokeDistance (meters)'])
	yrange = y_axis_range(df.ix[:,' StrokeDistance (meters)'],
			      ultimate = [5,15])
	ax6.axis([0,end_dist,yrange[0],yrange[1]])
	ax6.set_xlabel('Distance (m)')
	ax6.set_xticks(range(1000,end_dist,1000))
	ax6.set_ylabel('Stroke Distance (m)')
#	ax6.set_yticks(np.arange(5.5,11.5,0.5))
	grid(True)
	

	plt.subplots_adjust(hspace=0)

	plt.show()
	print "done"
    

    def plottime_otw(self):
	""" Creates two images containing interesting plots

	x-axis is time

	Used with OTW data (no Power plot)
	

	"""
	
	df = self.df

	# time increments for bar chart
	time_increments = df.ix[:,' ElapsedTime (sec)'].diff()
	time_increments[0] = time_increments[1]
	


	fig1 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- HR / Pace / Rate "

	# First panel, hr
	ax1 = fig1.add_subplot(3,1,1)
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut2'],
		width=time_increments,
		color='gray', ec='gray')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_ut1'],
		width=time_increments,
		color='y',ec='y')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_at'],
		width=time_increments,
		color='g',ec='g')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_tr'],
		width=time_increments,
		color='blue',ec='blue')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_an'],
		width=time_increments,
		color='violet',ec='violet')
	ax1.bar(df.ix[:,'TimeStamp (sec)'],df.ix[:,'hr_max'],
		width=time_increments,
		color='r',ec='r')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut2'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_ut1'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_at'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_tr'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_an'],color='k')
	ax1.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,'lim_max'],color='k')
	ax1.text(5,self.rower.ut2+1.5,"UT2",size=8)
	ax1.text(5,self.rower.ut1+1.5,"UT1",size=8)
	ax1.text(5,self.rower.at+1.5,"AT",size=8)
	ax1.text(5,self.rower.tr+1.5,"TR",size=8)
	ax1.text(5,self.rower.an+1.5,"AN",size=8)
	ax1.text(5,self.rower.max+1.5,"MAX",size=8)

	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	ax1.axis([0,end_time,100,1.1*self.rower.max])
	ax1.set_xticks(range(0,end_time,300))
	ax1.set_ylabel('BPM')
	ax1.set_yticks(range(110,190,10))
	ax1.set_title(fig_title)
	timeTickFormatter = NullFormatter()
	ax1.xaxis.set_major_formatter(timeTickFormatter)

	grid(True)

	# Second Panel, Pace
	ax2 = fig1.add_subplot(3,1,2)
	ax2.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Stroke500mPace (sec/500m)'])
	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,190])
	ax2.axis([0,end_time,yrange[1],yrange[0]])
	ax2.set_xticks(range(0,end_time,300))
	ax2.set_ylabel('(sec/500)')
#	ax2.set_yticks(range(175,90,-5))
	# ax2.set_title('Pace')
	grid(True)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax2.xaxis.set_major_formatter(timeTickFormatter)
	ax2.yaxis.set_major_formatter(majorFormatter)

	# Third Panel, rate
	ax3 = fig1.add_subplot(3,1,3)
	ax3.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Cadence (stokes/min)'])
#	rate_ewma = pd.ewma(df,span=20)
#	ax3.plot(rate_ewma.ix[:,'TimeStamp (sec)'],
#		 rate_ewma.ix[:,' Cadence (stokes/min)'])
	ax3.axis([0,end_time,14,40])
	ax3.set_xticks(range(0,end_time,300))
	ax3.set_xlabel('Time (sec)')
	ax3.set_ylabel('SPM')
	ax3.set_yticks(range(16,40,2))
	# ax3.set_title('Rate')
	ax3.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)


	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax3.set_xlabel('Time (h:m)')
	ax3.xaxis.set_major_formatter(majorTimeFormatter)
	plt.subplots_adjust(hspace=0)
	
	fig2 = plt.figure(figsize=(12,10))
	fig_title = "Input File:  "+self.readfilename+" --- Stroke Metrics"

	# Top plot is pace
	ax5 = fig2.add_subplot(2,1,1)
	ax5.plot(df.ix[:,'TimeStamp (sec)'],df.ix[:,' Stroke500mPace (sec/500m)'])
	yrange = y_axis_range(df.ix[:,' Stroke500mPace (sec/500m)'],
			      ultimate = [85,190])
	end_time = int(df.ix[df.shape[0]-1,'TimeStamp (sec)'])
	ax5.axis([0,end_time,yrange[1],yrange[0]])
	ax5.set_xticks(range(0,end_time,300))
	ax5.set_ylabel('(sec/500)')
#	ax5.set_yticks(range(175,90,-5))
	grid(True)
	ax5.set_title(fig_title)
	majorFormatter = FuncFormatter(format_pace_tick)
	majorLocator = (5)
	ax5.xaxis.set_major_formatter(timeTickFormatter)
	ax5.yaxis.set_major_formatter(majorFormatter)

	# next we plot the drive length
	ax6 = fig2.add_subplot(2,1,2)
	ax6.plot(df.ix[:,'TimeStamp (sec)'],
		 df.ix[:,' StrokeDistance (meters)'])
	yrange = y_axis_range(df.ix[:,' StrokeDistance (meters)'],
			      ultimate = [5,15])

	ax6.axis([0,end_time,yrange[0],yrange[1]])
	ax6.set_xticks(range(0,end_time,300))
	ax6.set_xlabel('Time (sec)')
	ax6.set_ylabel('Stroke Distance (m)')
#	ax6.set_yticks(np.arange(5.5,11.5,0.5))
	ax6.xaxis.set_major_formatter(timeTickFormatter)
	grid(True)


	majorTimeFormatter = FuncFormatter(format_time_tick)
	majorLocator = (15*60)
	ax6.set_xlabel('Time (h:m)')
	ax6.xaxis.set_major_formatter(majorTimeFormatter)
	plt.subplots_adjust(hspace=0)

	plt.show()

	self.piechart()
	
	print "done"

    def piechart(self):
	""" Figure 3 - Heart Rate Time in band.
	This is not as simple as just totalling up the
	hits for each band of HR.  Since each data point represents
	a different increment of time.  This loop scans through the
	HR data and adds that incremental time in each band

	"""

	df = self.df
	df.sort_values(by=' ElapsedTime (sec)',ascending = 1)
	number_of_rows = self.number_of_rows

	time_increments = df.ix[:,'TimeStamp (sec)'].diff()
	time_increments[0] = time_increments[1]
	
	time_in_zone = np.zeros(6)
	for i in range(number_of_rows):
	    if df.ix[i,' HRCur (bpm)'] <= self.rower.ut2:
		time_in_zone[0] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.ut1:
		time_in_zone[1] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.at:
		time_in_zone[2] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.tr:
		time_in_zone[3] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.an:
		time_in_zone[4] += time_increments[i]
	    else:
		time_in_zone[5] += time_increments[i]
		
	# print(time_in_zone)
	wedge_labels = ['ut2','ut2','ut1','at','tr','an']
	for i in range(len(wedge_labels)):
	    min = int(time_in_zone[i]/60.)
	    sec = int(time_in_zone[i] - min*60.)
	    secstr=str(sec).zfill(2)
	    s = "%d:%s" % (min,secstr)
	    wedge_labels[i] = wedge_labels[i]+"\n"+s
	
	# print(wedge_labels)
	fig2 = plt.figure(figsize=(5,5))
	fig_title = "Input File:  "+self.readfilename+" --- HR Time in Zone"
	ax9 = fig2.add_subplot(1,1,1)
	ax9.pie(time_in_zone,
		labels=wedge_labels,
		colors=['gray','gold','limegreen','dodgerblue','m','r'],
		autopct='%4.1f%%',
		pctdistance=0.8,
		counterclock=False,
		startangle=90.0)

	plt.show()
	return 1

    def get_piechart(self,title):
	""" Figure 3 - Heart Rate Time in band.
	This is not as simple as just totalling up the
	hits for each band of HR.  Since each data point represents
	a different increment of time.  This loop scans through the
	HR data and adds that incremental time in each band

	"""

	df = self.df
	number_of_rows = self.number_of_rows

	time_increments = df.ix[:,'TimeStamp (sec)'].diff()
	time_increments[0] = time_increments[1]
	
	time_in_zone = np.zeros(6)
	for i in range(number_of_rows):
	    if df.ix[i,' HRCur (bpm)'] <= self.rower.ut2:
		time_in_zone[0] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.ut1:
		time_in_zone[1] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.at:
		time_in_zone[2] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.tr:
		time_in_zone[3] += time_increments[i]
	    elif df.ix[i,' HRCur (bpm)'] <= self.rower.an:
		time_in_zone[4] += time_increments[i]
	    else:
		time_in_zone[5] += time_increments[i]
		
	# print(time_in_zone)
	wedge_labels = ['ut2','ut2','ut1','at','tr','an']
	for i in range(len(wedge_labels)):
	    min = int(time_in_zone[i]/60.)
	    sec = int(time_in_zone[i] - min*60.)
	    secstr=str(sec).zfill(2)
	    s = "%d:%s" % (min,secstr)
	    wedge_labels[i] = wedge_labels[i]+"\n"+s
	
	# print(wedge_labels)
#	fig2 = plt.figure(figsize=(5,5))
	fig2 = figure.Figure(figsize=(5,5))
	fig_title = title
	ax9 = fig2.add_subplot(1,1,1)
	ax9.pie(time_in_zone,
		labels=wedge_labels,
		colors=['gray','gold','limegreen','dodgerblue','m','r'],
		autopct='%4.1f%%',
		pctdistance=0.8,
		counterclock=False,
		startangle=90.0)


	return fig2

    def uploadtoc2(self,
		   comment="uploaded by rowingdata tool\n",
		   rowerFile="defaultrower.txt"):
	""" Upload your row to the Concept2 logbook

	Will ask for username and password if not known
	Will offer to store username and password locally for you.
	This is not mandatory

	This just fills the online logbook form. It may break if Concept2
	changes their website. I am waiting for a Concept2 Logbook API

	"""

	comment+="version %s.\n" % __version__
	comment+=self.readfilename

	# prepare the needed data
	# Date
	datestring = "{mo:0>2}/{dd:0>2}/{yr}".format(
	    yr = self.rowdatetime.year,
	    mo = self.rowdatetime.month,
	    dd = self.rowdatetime.day
	    )

	rowtypenr = [1]
	weightselect = ["L"]

	# row type
	availabletypes = getrowtype()
	try:
	    rowtypenr = availabletypes[self.rowtype]
	except KeyError:
	    rowtypenr = [1]


	# weight
	if (self.rower.weightcategory.lower()=="lwt"):
	    weightselect = ["L"]
	else:
	    weightselect = ["H"]

	df = self.df

	# total dist, total time, avg pace, avg hr, max hr, avg dps

	totaldist = df['cum_dist'].max()
	totaltime = df['TimeStamp (sec)'].max()
	avgpace = 500*totaltime/totaldist
	avghr = df[' HRCur (bpm)'].mean()
	maxhr = df[' HRCur (bpm)'].max()
	avgspm = df[' Cadence (stokes/min)'].mean()
	avgdps = totaldist/(totaltime*avgspm/60.)

	hour=int(totaltime/3600)
	min=int((totaltime-hour*3600.)/60)
	sec=int((totaltime-hour*3600.-min*60.))
	tenth=int(10*(totaltime-hour*3600.-min*60.-sec))

	# log in to concept2 log, ask for password if it isn't known
	print "login to concept2 log"
	save_user = "y"
	save_pass = "y"
	if self.rower.c2username == "":
	    save_user = "n"
	    self.rower.c2username = raw_input('C2 user name:')
	    save_user = raw_input('Would you like to save your username (y/n)? ')
	    
	if self.rower.c2password == "":
	    save_pass = "n"
	    self.rower.c2password = getpass.getpass('C2 password:')
	    save_pass = raw_input('Would you like to save your password (y/n)? ')

	# try to log in to logbook
	br = mechanize.Browser()
	loginpage = br.open("http://log.concept2.com/login")

	# the login is the first form
	br.select_form(nr=0)
	# set user name
	usercntrl = br.form.find_control("username")
	usercntrl.value = self.rower.c2username

	pwcntrl = br.form.find_control("password")
	pwcntrl.value = self.rower.c2password

	response = br.submit()
	if "Incorrect" in response.read():
	    print "Incorrect username/password combination"
	    print ""
	else:
	    # continue
	    print "login successful"
	    print ""
	    br.select_form(nr=0)

	    br.form['type'] = rowtypenr
	    print "setting type to "+self.rowtype

	    datecntrl = br.form.find_control("date")
	    datecntrl.value = datestring
	    print "setting date to "+datestring

	    distcntrl = br.form.find_control("distance")
	    distcntrl.value = str(int(totaldist))
	    print "setting distance to "+str(int(totaldist))

	    hrscntrl = br.form.find_control("hours")
	    hrscntrl.value = str(hour)
	    mincntrl = br.form.find_control("minutes")
	    mincntrl.value = str(min)
	    secscntrl = br.form.find_control("seconds")
	    secscntrl.value = str(sec)
	    tenthscntrl = br.form.find_control("tenths")
	    tenthscntrl.value = str(tenth)

	    print "setting duration to {hour} hours, {min} minutes, {sec} seconds, {tenth} tenths".format(
		hour = hour,
		min = min,
		sec  = sec,
		tenth = tenth
		)

	    br.form['weight_class'] = weightselect

	    print "Setting weight class to "+self.rower.weightcategory+"("+weightselect[0]+")"

	    commentscontrol = br.form.find_control("comments")
	    commentscontrol.value = comment
	    print "Setting comment to:"
	    print comment

	    print ""

	    res = br.submit()

	    if "New workout added" in res.read():

		# workout added
		print "workout added"
	    else:
		print "something went wrong"

	if save_user == "n":
	    self.rower.c2username = ''
	    print "forgetting user name"
	if save_pass == "n":
	    self.rower.c2password = ''
	    print "forgetting password"


	if (save_user == "y" or save_pass == "y"):
	    self.rower.write(rowerFile)
	    

	print "done"


def dorowall(readFile="testdata",window_size=20):
    """ Used if you have CrewNerd TCX and summary CSV with the same file name

    Creates all the plots and spits out a text summary (and copies it
    to the clipboard too!)

    """

    tcxFile = readFile+".TCX"
    csvsummary = readFile+".CSV"
    csvoutput = readFile+"_data.CSV"

    tcx = rowingdata.TCXParser(tcxFile)
    tcx.write_csv(csvoutput,window_size=window_size)

    res = rowingdata.rowingdata(csvoutput)
    res.plotmeters_otw()

    sumdata = rowingdata.summarydata(csvsummary)
    sumdata.shortstats()

    sumdata.allstats()
