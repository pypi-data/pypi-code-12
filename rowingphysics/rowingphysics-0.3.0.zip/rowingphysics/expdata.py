import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.pyplot import grid
from matplotlib import figure
from matplotlib.ticker import MultipleLocator,FuncFormatter,NullFormatter

import rowingphysics

def format_time_tick(x,pos=None):
	hour=int(x/3600)
	min=int((x-hour*3600.)/60)
	min_str=str(min).zfill(2)
	template='%d:%s'
	return template % (hour,min_str)

def format_time(x,pos=None):


    min = int(x/60.)
    sec = int(x-min*60)

    str1 = "{min:0>2}:{sec:0>4.1f}".format(
	min=min,
	sec=sec,
	)

    return str1

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

def tempofromergsplit(ergsplit):
    tempo1 = 25.
    tempo2 = 35.

    split1 = 120.
    split2 = 85.

    ratio = (ergsplit-split2)/(split1-split2)

    tempo = tempo2+ratio*(tempo1-tempo2)

    return tempo

def splitvalues(s):
    min, sec = map(int, s.split(':'))

    return [min,sec]

def rawtoseconds(raw):
    r = np.array(map(splitvalues,raw))
    thetime = 60.*r[:,0]+r[:,1]
    return thetime

def plotdata(filename,r,rg,erg):
    expdata_raw = pd.read_csv(filename)

    ergtime = rawtoseconds(expdata_raw['erg score'])/4.

    fifty = rawtoseconds(expdata_raw['50kg'])/4.
    sixty = rawtoseconds(expdata_raw['60kg'])/4.
    seventy = rawtoseconds(expdata_raw['70kg'])/4.
    eighty = rawtoseconds(expdata_raw['80kg'])/4.
    ninety = rawtoseconds(expdata_raw['90kg'])/4.
    hundred = rawtoseconds(expdata_raw['100kg'])/4.
    hundredten = rawtoseconds(expdata_raw['110kg'])/4.

    ratio = 0.5

    print '50kg'

    r.mc = 50.0
    r.tempo = 30.

    otwsplit50kg = []

    for ergscore in expdata_raw['erg score']:
	print ergscore
	mins, secs = splitvalues(ergscore)
	ergsplit = (60.0*mins+secs)/4.
	r.tempo = tempofromergsplit(ergsplit)
	ergsplitmin = int(ergsplit) / 60
	ergsplitsec = ergsplit-60*ergsplitmin

	res = rowingphysics.ergtopower(ergsplitmin,ergsplitsec,ratio,r,erg)
	totalpower = res[0]
	ergpower = res[1]
	res = rowingphysics.constantwatt(totalpower,r,rg)
	otwsplit = 500./res[1]
	otwsplit50kg.append(otwsplit)

    print '70kg'

    r.mc = 70.0

    otwsplit70kg = []

    for ergscore in expdata_raw['erg score']:
	print ergscore
	mins, secs = splitvalues(ergscore)
	ergsplit = (60.0*mins+secs)/4.
	r.tempo = tempofromergsplit(ergsplit)
	ergsplitmin = int(ergsplit) / 60
	ergsplitsec = ergsplit-60*ergsplitmin

	res = rowingphysics.ergtopower(ergsplitmin,ergsplitsec,ratio,r,erg)
	totalpower = res[0]
	ergpower = res[1]
	res = rowingphysics.constantwatt(totalpower,r,rg)
	otwsplit = 500./res[1]
	otwsplit70kg.append(otwsplit)

    print '90kg'

    r.mc = 90.0

    otwsplit90kg = []

    for ergscore in expdata_raw['erg score']:
	print ergscore
	mins, secs = splitvalues(ergscore)
	ergsplit = (60.0*mins+secs)/4.
	r.tempo = tempofromergsplit(ergsplit)
	ergsplitmin = int(ergsplit) / 60
	ergsplitsec = ergsplit-60*ergsplitmin

	res = rowingphysics.ergtopower(ergsplitmin,ergsplitsec,ratio,r,erg)
	totalpower = res[0]
	ergpower = res[1]
	res = rowingphysics.constantwatt(totalpower,r,rg)
	otwsplit = 500./res[1]
	otwsplit90kg.append(otwsplit)

    print '110kg'

    r.mc = 110.0

    otwsplit110kg = []

    for ergscore in expdata_raw['erg score']:
	print ergscore
	mins, secs = splitvalues(ergscore)
	ergsplit = (60.0*mins+secs)/4.
	r.tempo = tempofromergsplit(ergsplit)
	ergsplitmin = int(ergsplit) / 60
	ergsplitsec = ergsplit-60*ergsplitmin

	res = rowingphysics.ergtopower(ergsplitmin,ergsplitsec,ratio,r,erg)
	totalpower = res[0]
	ergpower = res[1]
	res = rowingphysics.constantwatt(totalpower,r,rg)
	otwsplit = 500./res[1]
	otwsplit110kg.append(otwsplit)

    # making the plot

    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(1,1,1)
    ax.plot(ergtime,fifty,color='k')
    ax.plot(ergtime,otwsplit50kg,color='k')
    ax.plot(ergtime,sixty,color='r')
    ax.plot(ergtime,seventy,color='g')
    ax.plot(ergtime,otwsplit70kg,color='g')
    ax.plot(ergtime,eighty,color='b')
    ax.plot(ergtime,ninety,color='c')
    ax.plot(ergtime,otwsplit90kg,color='c')
    ax.plot(ergtime,hundred,color='m')
    ax.plot(ergtime,hundredten,color='y')
    ax.plot(ergtime,otwsplit110kg,color='y')

    ax.axis([125,75,150,85])
    ax.set_xticks(range(85,125,10))
    ax.set_xlabel('Erg split')
    ax.set_ylabel('OTW split')
    ax.set_title(filename)
    ax.set_yticks(range(85,150,10))
    timeTickFormatter = NullFormatter()

    majorTimeFormatter = FuncFormatter(format_time_tick)
    majorLocator = (15*60)
    ax.xaxis.set_major_formatter(majorTimeFormatter)

    majorFormatter = FuncFormatter(format_pace_tick)
    majorLocator = (5)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.yaxis.set_major_formatter(majorFormatter)

    ax.legend(['50kg','50kg  OTW','60kg','70kg','70kg OTW',
	       '80kg','90kg','90kg OTW',
	       '100kg','110kg','110kg OTW'],
	      prop={'size':10},loc=0)

    grid(True)

    fig.show()
